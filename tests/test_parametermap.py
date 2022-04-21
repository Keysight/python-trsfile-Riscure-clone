from unittest import TestCase

from trsfile.parametermap import TraceSetParameterMap, TraceParameterDefinitionMap, TraceParameterMap
from trsfile.standardparameters import StandardTraceSetParameters, StandardTraceParameters
from trsfile.traceparameter import *


class TestTraceSetParameterMap(TestCase):
    SERIALIZED_MAP = b'\x09\x00' \
                     b'\x06\x00param1\x31\x05\x00\x01\x00\x00\x01\x01' \
                     b'\x06\x00param2\x01\x06\x00\x00\x01\x7f\x80\xfe\xff' \
                     b'\x06\x00param3\x02\x07\x00\x00\x00\x01\x00\xff\xff\xff\x00\x00\x01\x00\x80\xff\x7f' \
                     b'\x06\x00param4\x04\x04\x00\xff\xff\xff\xff\x01\x00\x00\x00\xff\xff\xff\x7f\x00\x00\x00\x80' \
                     b'\x06\x00param5\x08\x04\x00\xff\xff\xff\xff\xff\xff\xff\xff\x01\x00\x00\x00\x00\x00\x00\x00' \
                     b'\xff\xff\xff\xff\xff\xff\xff\x7f\x00\x00\x00\x00\x00\x00\x00\x80' \
                     b'\x06\x00param6\x14\x03\x00\x00\x00\x00\xbf\x00\x00\x00\x3f\x00\x24\x74\x49' \
                     b'\x06\x00param7\x18\x03\x00\x00\x00\x00\x00\x00\x00\xe0\xbf\x00\x00\x00\x00\x00\x00\xe0\x3f' \
                     b'\x00\x00\x00\x00\x80\x84\x2e\x41' \
                     b'\x06\x00param8\x20\x2d\x00The quick brown fox jumped over the lazy dog.' \
                     b'\x06\x00\xe4\xb8\xad\xe6\x96\x87\x20\x0f\x00\xe4\xbd\xa0\xe5\xa5\xbd\xef\xbc\x8c\xe4\xb8' \
                     b'\x96\xe7\x95\x8c'

    @staticmethod
    def create_tracesetparametermap() -> TraceSetParameterMap:
        result = TraceSetParameterMap()
        result['param1'] = BooleanArrayParameter([True, False, False, True, True])
        result['param2'] = ByteArrayParameter([0, 1, 127, 128, 254, 255])
        result['param3'] = ShortArrayParameter([0, 1, -1, 255, 256, -32768, 32767])
        result['param4'] = IntegerArrayParameter([-1, 1, 0x7fffffff, -0x80000000])
        result['param5'] = LongArrayParameter([-1, 1, 0x7fffffffffffffff, -0x8000000000000000])
        result['param6'] = FloatArrayParameter([-0.5, 0.5, 1e6])
        result['param7'] = DoubleArrayParameter([-0.5, 0.5, 1e6])
        result['param8'] = StringParameter('The quick brown fox jumped over the lazy dog.')
        result['中文'] = StringParameter('你好，世界')
        return result

    def test_deserialize(self):
        param_map = TraceSetParameterMap.deserialize(BytesIO(self.SERIALIZED_MAP))
        deserialized = self.create_tracesetparametermap()
        self.assertDictEqual(param_map, deserialized)

    def test_serialize(self):
        param_map = self.create_tracesetparametermap()
        serialized = param_map.serialize()
        self.assertEqual(serialized, self.SERIALIZED_MAP)

    def test_add_parameter(self):
        param_map = TraceSetParameterMap()
        param_map.add_parameter('param1', [True, False, False, True, True])
        param_map.add_parameter('param2', bytearray([0, 1, 127, 128, 254, 255]))
        param_map.add_parameter('param3', [0, 1, -1, 255, 256, -32768, 32767])
        param_map.add_parameter('param4', [-1, 1, 0x7fffffff, -0x80000000])
        param_map.add_parameter('param5', [-1, 1, 0x7fffffffffffffff, -0x8000000000000000])
        # python floats default to doubles, so add Float parameters the old-fashioned way:
        param_map['param6'] = FloatArrayParameter([-0.5, 0.5, 1e6])
        param_map.add_parameter('param7', [-0.5, 0.5, 1e6])
        param_map.add_parameter('param8', 'The quick brown fox jumped over the lazy dog.')
        param_map.add_parameter('中文', '你好，世界')
        expected_map = self.create_tracesetparametermap()
        self.assertDictEqual(param_map, expected_map)

        # A single integer should be stored in an array:
        param_map.add_parameter('param9', 1)
        self.assertEqual(param_map['param9'], IntegerArrayParameter([1]))

        with self.assertRaises(TypeError):
            param_map.add_parameter('param10', [False, 0, 'None'])
        with self.assertRaises(TypeError):
            param_map.add_parameter('param10', None)
        with self.assertRaises(TypeError):
            param_map.add_parameter('param10', ['The', 'quick', 'brown', 'fox', 'jumped', 'over', 'the', 'lazy', 'dog'])
        with self.assertRaises(TypeError):
            param_map.add_parameter('param10', [])

    def test_add_standard_parameter(self):
        param_map1 = TraceSetParameterMap()
        param_map1.add_standard_parameter(StandardTraceSetParameters.KEY,
                                          bytes.fromhex('cafebabedeadbeef0102030405060708'))
        param_map2 = TraceSetParameterMap()
        param_map2.add_parameter('KEY', bytes.fromhex('cafebabedeadbeef0102030405060708'))
        self.assertDictEqual(param_map1, param_map2)

        # Verify that standard trace set parameters enforce a specific type
        with self.assertRaises(TypeError):
            param_map1.add_standard_parameter(StandardTraceSetParameters.KEY, 'cafebabedeadbeef0102030405060708')
        # Type checking even occurs when adding a parameter with the id of a standard trace set parameter
        with self.assertRaises(TypeError):
            param_map1.add_parameter('KEY', 'cafebabedeadbeef0102030405060708')


class TestTraceParameterDefinitionMap(TestCase):
    SERIALIZED_DEFINITION = b'\x03\x00' \
                            b'\x05\x00INPUT\x01\x10\x00\x00\x00' \
                            b'\x05\x00TITLE\x20\x0d\x00\x10\x00' \
                            b'\x06\x00\xe4\xb8\xad\xe6\x96\x87\x20\x0f\x00\x1d\x00'

    @staticmethod
    def create_parameterdefinitionmap() -> TraceParameterDefinitionMap:
        param_map = TraceParameterDefinitionMap()
        param_map['INPUT'] = TraceParameterDefinition(ParameterType.BYTE, 16, 0)
        param_map['TITLE'] = TraceParameterDefinition(ParameterType.STRING, 13, 16)
        param_map['中文'] = TraceParameterDefinition(ParameterType.STRING, 15, 29)
        return param_map

    @staticmethod
    def create_traceparametermap() -> TraceParameterMap:
        param_map = TraceParameterMap()
        param_map['INPUT'] = ByteArrayParameter(bytes.fromhex('cafebabedeadbeef0102030405060708'))
        param_map['TITLE'] = StringParameter('Hello, world!')
        param_map['中文'] = StringParameter('你好，世界')
        return param_map

    def test_get_total_size(self):
        size = self.create_parameterdefinitionmap().get_total_size()
        self.assertEqual(size, 44)

    def test_deserialize(self):
        self.assertDictEqual(TraceParameterDefinitionMap.deserialize(BytesIO(self.SERIALIZED_DEFINITION)),
                             self.create_parameterdefinitionmap())

    def test_serialize(self):
        self.assertEqual(self.create_parameterdefinitionmap().serialize(),
                         self.SERIALIZED_DEFINITION)

    def test_from_trace_params(self):
        param_map = TestTraceParameterDefinitionMap.create_traceparametermap()
        map_from_trace_params = TraceParameterDefinitionMap.from_trace_parameter_map(param_map)
        self.assertDictEqual(self.create_parameterdefinitionmap(), map_from_trace_params)


class TestTraceParameterMap(TestCase):
    CAFEBABE = bytes.fromhex('cafebabedeadbeef0102030405060708')
    SERIALIZED_MAP = CAFEBABE + \
                     b'Hello, world!' \
                     b'\xe4\xbd\xa0\xe5\xa5\xbd\xef\xbc\x8c\xe4\xb8\x96\xe7\x95\x8c'

    @staticmethod
    def create_parametermap() -> TraceParameterMap:
        param_map = TraceParameterMap()
        param_map['IN'] = ByteArrayParameter(list(TestTraceParameterMap.CAFEBABE))
        param_map['TITLE'] = StringParameter('Hello, world!')
        param_map['中文'] = StringParameter('你好，世界')
        return param_map

    def test_deserialize(self):
        self.assertDictEqual(
            TraceParameterMap.deserialize(self.SERIALIZED_MAP,
                                          TestTraceParameterDefinitionMap.create_parameterdefinitionmap()),
            self.create_parametermap())

    def test_serialize(self):
        self.assertEqual(self.SERIALIZED_MAP, self.create_parametermap().serialize())

    def test_add_parameter(self):
        param_map = TraceParameterMap()
        param_map.add_parameter('IN', TestTraceParameterMap.CAFEBABE)
        param_map.add_parameter('TITLE', 'Hello, world!')
        param_map.add_parameter('中文', '你好，世界')
        expected_map = self.create_parametermap()
        self.assertDictEqual(param_map, expected_map)

        # A single boolean should be stored in an array:
        param_map.add_parameter('HAS_KEY', False)
        self.assertEqual(param_map['HAS_KEY'], BooleanArrayParameter([False]))

        with self.assertRaises(TypeError):
            param_map.add_parameter('OUT', [False, 0, 'None'])
        with self.assertRaises(TypeError):
            param_map.add_parameter('OUT', None)
        with self.assertRaises(TypeError):
            param_map.add_parameter('OUT', [bytes.fromhex('cafebabedeadbeef'), bytes.fromhex('0102030405060708')])
        with self.assertRaises(TypeError):
            param_map.add_parameter('OUT', [])

    def test_add_standard_parameter(self):
        param_map1 = TraceParameterMap()
        param_map1.add_standard_parameter(StandardTraceParameters.INPUT,
                                          bytes.fromhex('cafebabedeadbeef0102030405060708'))
        param_map2 = TraceParameterMap()
        param_map2.add_parameter('INPUT', bytes.fromhex('cafebabedeadbeef0102030405060708'))
        self.assertDictEqual(param_map1, param_map2)

        # Verify that standard trace parameters enforce a specific type
        with self.assertRaises(TypeError):
            param_map1.add_standard_parameter(StandardTraceParameters.INPUT, 'cafebabedeadbeef0102030405060708')
        # Type checking even occurs when adding a parameter with the id of a standard trace parameter
        with self.assertRaises(TypeError):
            param_map1.add_parameter('INPUT', 'cafebabedeadbeef0102030405060708')
