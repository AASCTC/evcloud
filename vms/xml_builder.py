from utils import errors
from .xml import XMLEditor


class VmXMLBuilder:
    @staticmethod
    def xml_edit_vcpu(xml_desc: str, vcpu: int):
        """
        修改 xml中vcpu节点内容

        :param xml_desc: 定义虚拟机的xml内容
        :param vcpu: 虚拟cpu数
        :return:
            xml: str    # success

        :raise:  VmError
        """
        xml = XMLEditor()
        if not xml.set_xml(xml_desc):
            raise errors.VmError(msg='xml文本无效')

        root = xml.get_root()
        try:
            root.getElementsByTagName('vcpu')[0].firstChild.data = vcpu
        except Exception as e:
            raise errors.VmError(msg='修改xml文本vcpu节点错误')

        return root.toxml()

    @staticmethod
    def xml_edit_mem(xml_desc: str, mem: int):
        """
        修改xml中mem节点内容

        :param xml_desc: 定义虚拟机的xml内容
        :param mem: 修改内存大小
        :return:
            xml: str    # success

        :raise:  VmError
        """
        xml = XMLEditor()
        if not xml.set_xml(xml_desc):
            raise errors.VmError(msg='xml文本无效')
        try:
            root = xml.get_root()
            node = root.getElementsByTagName('memory')[0]
            node.attributes['unit'].value = 'GiB'
            node.firstChild.data = mem

            node = root.getElementsByTagName('currentMemory')[0]
            node.attributes['unit'].value = 'GiB'
            node.firstChild.data = mem

            return root.toxml()
        except Exception as e:
            raise errors.VmError(msg='修改xml文本memory节点错误')

    def get_vm_vdisk_dev_list(self, xml_desc: str):
        """
        获取虚拟机所有硬盘的dev

        :param xml_desc: 虚拟机xml
        :return:
            (disk:list, dev:list)    # disk = [disk_uuid, disk_uuid, ]; dev = ['vda', 'vdb', ]

        :raises: VmError
        """
        dev_list = []
        disk_list = []
        xml = XMLEditor()
        if not xml.set_xml(xml_desc):
            raise errors.VmError(msg='虚拟机xml文本无效')

        root = xml.get_root()
        devices = root.getElementsByTagName('devices')[0].childNodes
        for d in devices:
            if d.nodeName == 'disk':
                for disk_child in d.childNodes:
                    if disk_child.nodeName == 'source':
                        pool_disk = disk_child.getAttribute('name')
                        disk = pool_disk.split('/')[-1]
                        disk_list.append(disk)
                    if disk_child.nodeName == 'target':
                        dev_list.append(disk_child.getAttribute('dev'))

        return disk_list, dev_list

    @staticmethod
    def new_vdisk_dev(dev_list: list):
        """
        顺序从vda - vdz中获取下一个不包含在dev_list中的的dev字符串

        :param dev_list: 已使用的dev的list
        :return:
            str     # success
            None    # 没有可用的dev了
        """
        # 从vdb开始，系统xml模板中系统盘驱动和硬盘一样为virtio时，硬盘使用vda会冲突错误
        for i in range(1, 26):
            dev = 'vd' + chr(ord('a') + i % 26)
            if dev not in dev_list:
                return dev

        return None

    @staticmethod
    def xml_remove_sys_disk_auth(xml_desc: str):
        """
        去除vm xml中系统盘节点ceph认证的auth

        :param xml_desc: 定义虚拟机的xml内容
        :return:
            xml: str    # success

        :raise:  VmError
        """
        xml = XMLEditor()
        if not xml.set_xml(xml_desc):
            raise errors.VmError(msg='虚拟机xml文本无效')

        root = xml.get_root()
        devices = root.getElementsByTagName('devices')
        if not devices:
            raise errors.VmError(msg='虚拟机xml文本无效, 未找到devices节点')

        disks = devices[0].getElementsByTagName('disk')
        if not disks:
            raise errors.VmError(msg='虚拟机xml文本无效, 未找到devices>disk节点')
        disk = disks[0]
        auth = disk.getElementsByTagName('auth')
        if not auth:
            return xml_desc

        disk.removeChild(auth[0])
        return root.toxml()

    @staticmethod
    def xml_remove_huge_page(xml_desc: str):
        """
        去除vm xml中大页内存配置

        :param xml_desc: 定义虚拟机的xml内容
        :return:
            xml: str    # success

        :raise:  VmError
        """
        xml = XMLEditor()
        if not xml.set_xml(xml_desc):
            raise errors.VmError(msg='虚拟机xml文本无效')

        root = xml.get_root()
        huge_page_node = root.getElementsByTagName('memoryBacking')
        if not huge_page_node:
            return xml_desc

        root.removeChild(huge_page_node[0])
        return root.toxml()

    @staticmethod
    def add_cpu_topology_xml(xml_desc: str, max_cpu_sockets: int, cores_num: int):
        """为cpu 添加 topology 节点

        topology： node-name
            sockets： cpu 卡槽  attr
            cores: cpu 核      attr
            threads: 线程      attr
        """

        if not max_cpu_sockets or not cores_num:
            return xml_desc

        xml = XMLEditor()
        if not xml.set_xml(xml_desc):
            raise errors.VmError(msg='虚拟机xml文本无效')

        node = xml.create_node(tag_name='topology',
                               atter_dict={'sockets': str(max_cpu_sockets), 'dies': "1", 'cores': str(cores_num),
                                           'threads': "1"})

        if not node:
            return xml_desc

        root = xml.get_root()
        cpu_node = root.getElementsByTagName('cpu')
        if not cpu_node:
            return xml_desc
        cpu_node[0].appendChild(node)
        return root.toxml()

    def build_vm_xml_desc(
            self, vm_uuid: str, mem: int, vcpu: int, vm_disk_name: str,
            image_xml_tpl: str, ceph_pool, mac_ip, is_image_vm=False, max_cpu_sockets=0):
        """
        构建虚拟机的xml
        :param vm_uuid:
        :param mem:
        :param vcpu:
        :param vm_disk_name: vm的系统盘镜像rbd名称
        :param image_xml_tpl: 创建虚拟机的xml模板字符串
        :param ceph_pool: 镜像所在的ceph pool
        :param mac_ip: MacIP实例
        :param max_cpu_sockets: cpu 颗数 将 vcpu 平均
        :return:
            xml: str
        """
        pool = ceph_pool
        pool_name = pool.pool_name
        ceph = pool.ceph
        xml_tpl = image_xml_tpl  # 创建虚拟机的xml模板字符串

        # mem参数单位为GB，根据xml模版中的单位进行换算
        xml = XMLEditor()
        if not xml.set_xml(xml_tpl):
            raise errors.VmError(msg='虚拟机xml模版内容无效')
        try:
            root = xml.get_root()
            node = root.getElementsByTagName('currentMemory')[0]
            if node.attributes['unit'].value == 'MiB':
                mem = mem * 1024
            elif node.attributes['unit'].value == 'GiB':
                pass
            elif node.attributes['unit'].value == 'KiB':
                mem = mem * 1024 * 1024
            else:
                raise errors.VmError(msg='虚拟机xml模版中的currentMemory单位必须为KiB、MiB或GiB')
        except Exception as e:
            raise errors.VmError(msg='虚拟机创建时单位换算发生错误')

        xml_desc = xml_tpl.format(name=vm_uuid, uuid=vm_uuid, mem=mem, vcpu=vcpu, ceph_uuid=ceph.uuid,
                                  ceph_pool=pool_name, diskname=vm_disk_name, ceph_username=ceph.username,
                                  ceph_hosts_xml=ceph.hosts_xml, mac=mac_ip.mac, bridge=mac_ip.vlan.br)

        if max_cpu_sockets > 0:
            try:
                cores_num = self.get_cpu_topology_cores(vcpu=vcpu, max_cpu_sockets=max_cpu_sockets)
            except Exception as e:
                raise errors.VmError(msg=f'分配cpu核数时报错：{str(e)}')

            if cores_num:
                xml_desc = self.add_cpu_topology_xml(xml_desc=xml_desc, max_cpu_sockets=max_cpu_sockets,
                                                     cores_num=cores_num)

        if not ceph.has_auth:
            xml_desc = self.xml_remove_sys_disk_auth(xml_desc)

        if is_image_vm:
            xml_desc = self.xml_remove_huge_page(xml_desc)

        return xml_desc

    def get_cpu_topology_cores(self, vcpu: int, max_cpu_sockets: int):
        """计算 topology 中的 cores 数 """

        if not isinstance(vcpu, int) or not isinstance(max_cpu_sockets, int):
            return None

        if max_cpu_sockets == 1:
            return vcpu

        elif vcpu >= max_cpu_sockets:
            remainder = vcpu % max_cpu_sockets
            if remainder == 0:
                """vcpu 是 max_cpu_sockets 倍数"""
                cores = vcpu // max_cpu_sockets
                return cores
            return None
        return None
