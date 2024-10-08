from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import Serializer
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from drf_yasg import openapi

from api.viewsets import CustomGenericViewSet
from compute.managers import CenterManager, GroupManager, ComputeError
from utils import errors as exceptions

from utils.permissions import APIIPPermission


class ComputeQuotaViewSet(CustomGenericViewSet):
    """
    可用资源配额类视图
    """
    permission_classes = [IsAuthenticated, APIIPPermission]
    pagination_class = None
    lookup_field = 'id'

    @swagger_auto_schema(
        operation_summary='获取可用总资源配额和已用配额信息',
        manual_parameters=[
            openapi.Parameter(
                name='mem_unit',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=False,
                description='内存计算单位（默认MB，可选GB）'
            ),
            openapi.Parameter(
                name='center_id',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True,
                description='数据中心'
            )
        ],
        responses={
            200: ''
        }
    )
    def list(self, request, *args, **kwargs):
        """
        获取可用总资源配额和已用配额信息

            http code 200:
            {
              "quota": {
                "mem_total": 251552,            # Mb
                "mem_allocated": 4096,
                "vcpu_total": 292,
                "vcpu_allocated": 5,
                "real_cpu": 100,
                "vm_created": 3,
                "vm_limit": 41,
                "ips_total": 5,
                "ips_used": 2,
                "ips_private":2,
                "ips_public":3,
              }
            }
        """
        mem_unit = str.upper(request.query_params.get('mem_unit', 'UNKNOWN'))
        center_id = request.query_params.get('center_id', None)

        if mem_unit not in ['GB', 'MB', 'UNKNOWN']:
            exc = exceptions.BadRequestError(msg='无效的内存单位, 正确格式为GB、MB或为空')
            return self.exception_response(exc)

        # 用户操作日志记录
        # user_operation_record.add_log(request=request, type=LogRecord.ASSETS, action_flag=LogRecord.SELECT,
        #                               operation_content='获取可用总资源配额和已用配额信息', remark='')
        try:
            center_id = int(center_id)
        except ValueError:
            return self.exception_response(
                exceptions.BadRequestError(msg='无效的数据中心id，值需要是一个正整数'))

        quota = GroupManager().compute_quota(user=request.user, center_id=center_id)

        if 'GB' == mem_unit:
            quota['mem_unit'] = 'GB'
        else:
            quota['mem_total'] = quota['mem_total'] * 1024
            quota['mem_allocated'] = quota['mem_allocated'] * 1024
            quota['mem_unit'] = 'MB'
        return Response(data={'quota': quota})

    # 汇总数据中心资源
    @swagger_auto_schema(
        operation_summary='全数据中心资源汇总',
        manual_parameters=[
            openapi.Parameter(
                name='mem_unit',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=False,
                description='内存计算单位（默认MB，可选GB）'
            )
        ],
        responses={
            200: ''
        }
    )
    @action(methods=['get'], detail=False, url_path=r'center', url_name='center')
    def center_compute_quota(self, request, *args, **kwargs):
        """
        获取所有数据中心资源配额信息

            http code 200:
                {
                  "quota": {
                    "mem_total": 37,  # 总内存
                    "mem_allocated": 1,  # 使用内存
                    "vcpu_total": 72,   # 总cpu
                    "vcpu_allocated": 1,  # 使用cpu
                    "real_cpu": 32,   #
                    "vm_created": 1,  # 创建的虚拟机数
                    "vm_limit": 22,
                    "ips_total": 9,  # IP 总数
                    "ips_used": 1,  # IP 使用数
                    "ips_private": 7,  # 内网IP数
                    "ips_public": 2,  # 公网IP数
                    "vdisk_num": 3,  # 云硬盘数
                    "vpn_total": 1,  # vpn总数
                    "vpn_active": 1,  # vpn 有效数
                    "vpn_invalid": 0,  # vpn 无效数
                    "ips_public_used": 0,  # 公网已使用IP数
                    "ips_private_used": 1, # 私网已使用IP数
                    "ips_rate": 0.11,  # ip 使用率
                    "cpu_rate": 0.01,  # cpu 使用率
                    "mem_rate": 0.03,  # 内存使用率
                    "vpn_online": 1,  # VPN 在线数
                    "mem_unit": "GB"
                  }
                }
        """
        mem_unit = str.upper(request.query_params.get('mem_unit', 'UNKNOWN'))
        if mem_unit not in ['GB', 'MB', 'UNKNOWN']:
            exc = exceptions.BadRequestError(msg='无效的内存单位, 正确格式为GB、MB或为空')
            return self.exception_response(exc)

        quota = CenterManager().get_stat_all_center(user=request.user)

        if 'GB' == mem_unit:
            quota['mem_unit'] = 'GB'
        else:
            quota['mem_total'] = quota['mem_total'] * 1024
            quota['mem_allocated'] = quota['mem_allocated'] * 1024
            quota['mem_unit'] = 'MB'
        return Response(data={'quota': quota})

    def get_serializer_class(self):
        return Serializer
