import pandas as pd

from unittest import TestCase
from pandas.util.testing import assert_frame_equal
from sfgad.modules.feature.vertex_activity_by_type import VertexActivityByType


class TestVertexActivityByType(TestCase):

    def setUp(self):
        self.df_1 = pd.DataFrame({'TIMESTAMP': ['2018-01-01 00:00:00', '2018-01-01 00:00:01', '2018-01-01 00:00:05'],
                                  'E_TYPE': ['LIKE', 'LIKE', 'MESSAGE'],
                                  'SRC_NAME': ['A', 'A', 'B'],
                                  'SRC_TYPE': ['NODE', 'NODE', 'NODE'],
                                  'DST_NAME': ['B', 'C', 'C'],
                                  'DST_TYPE': ['NODE', 'NODE', 'NODE']})
        self.df_1['TIMESTAMP'] = pd.to_datetime(self.df_1['TIMESTAMP'])

        self.df_2 = pd.DataFrame({'TIMESTAMP': ['2018-01-01 00:00:11', '2018-01-01 00:00:14', '2018-01-01 00:00:16'],
                                  'E_TYPE': ['LIKE', 'FRIENDSHIP', 'LIKE'],
                                  'SRC_NAME': ['A', 'A', 'A'],
                                  'SRC_TYPE': ['NODE', 'NODE', 'NODE'],
                                  'DST_NAME': ['B', 'D', 'D'],
                                  'DST_TYPE': ['NODE', 'NODE', 'NODE']})
        self.df_2['TIMESTAMP'] = pd.to_datetime(self.df_2['TIMESTAMP'])

        self.feature = VertexActivityByType(edge_types=['LIKE', 'MESSAGE', 'FRIENDSHIP'])

    def test_init(self):
        self.assertEqual(self.feature.names, ['VertexActivityByLIKE', 'VertexActivityByMESSAGE',
                                              'VertexActivityByFRIENDSHIP'])

    def test_process_vertices(self):
        # test the calculation of vertex activity by type in the 1. time step ('df_1')
        result_df = pd.DataFrame(data={'name': ['A', 'B', 'C'], 'VertexActivityByLIKE': [1, 1, 1],
                                       'VertexActivityByMESSAGE': [0, 1, 1], 'VertexActivityByFRIENDSHIP': [0, 0, 0]},
                                 columns=['name', 'VertexActivityByLIKE', 'VertexActivityByMESSAGE',
                                          'VertexActivityByFRIENDSHIP'])
        assert_frame_equal(self.feature.process_vertices(self.df_1, 1), result_df)

        # test the calculation of vertex degree difference by type in the 2. time step ('df_2')
        result_df_2 = pd.DataFrame(data={'name': ['A', 'B', 'D', 'C'], 'VertexActivityByLIKE': [1, 1, 1, 0],
                                         'VertexActivityByMESSAGE': [0, 0, 0, 0],
                                         'VertexActivityByFRIENDSHIP': [1, 0, 1, 0]},
                                   columns=['name', 'VertexActivityByLIKE', 'VertexActivityByMESSAGE',
                                            'VertexActivityByFRIENDSHIP'])
        assert_frame_equal(self.feature.process_vertices(self.df_2, 1), result_df_2)
