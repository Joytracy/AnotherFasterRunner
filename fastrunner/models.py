from django.db import models

# Create your models here.
from fastuser.models import BaseTable


class Project(BaseTable):
    """
    项目信息表
    """

    class Meta:
        verbose_name = "项目信息"
        db_table = "Project"

    name = models.CharField("项目名称", unique=True, null=False, max_length=100)
    desc = models.CharField("简要介绍", max_length=100, null=False)
    responsible = models.CharField("创建人", max_length=20, null=False)


class Debugtalk(models.Model):
    """
    驱动文件表
    """

    class Meta:
        verbose_name = "驱动库"
        db_table = "Debugtalk"

    code = models.TextField("python代码", default="# write you code", null=False)
    project = models.OneToOneField(to=Project, on_delete=models.CASCADE)


class Config(BaseTable):
    """
    环境信息表
    """

    class Meta:
        verbose_name = "环境信息"
        db_table = "Config"

    name = models.CharField("环境名称", null=False, max_length=100)
    body = models.TextField("主体信息", null=False)
    base_url = models.CharField("请求地址", null=False, max_length=100)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)


class API(BaseTable):
    """
    API信息表
    """

    class Meta:
        verbose_name = "接口信息"
        db_table = "API"

    env_type = (
        (0, "测试环境"),
        (1, "生产环境"),
        (2, "预发布 ")
    )
    tag = (
        (0, "还未调试"),
        (1, "手动成功"),
        (2, "调试失败"),
        (3, "自动成功")
    )
    name = models.CharField("接口名称", null=False, max_length=100, db_index=True)
    body = models.TextField("主体信息", null=False)
    url = models.CharField("请求地址", null=False, max_length=200, db_index=True)
    method = models.CharField("请求方式", null=False, max_length=10)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    relation = models.IntegerField("节点id", null=False)
    delete = models.IntegerField("是否删除", null=True, default=0)
    rig_id = models.IntegerField("网关API_id", null=True, db_index=True)
    rig_env = models.IntegerField("网关环境", choices=env_type, default=0)
    tag = models.IntegerField("API标签", choices=tag, default=0)


class Case(BaseTable):
    """
    用例信息表
    """

    class Meta:
        verbose_name = "用例信息"
        db_table = "Case"

    tag = (
        (1, "冒烟用例"),
        (2, "集成用例"),
        (3, "监控脚本")
    )
    name = models.CharField("用例名称", null=False, max_length=100)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    relation = models.IntegerField("节点id", null=False)
    length = models.IntegerField("API个数", null=False)
    tag = models.IntegerField("用例标签", choices=tag, default=2)


class CaseStep(BaseTable):
    """
    Test Case Step
    """

    class Meta:
        verbose_name = "用例信息 Step"
        db_table = "CaseStep"

    name = models.CharField("用例名称", null=False, max_length=100)
    body = models.TextField("主体信息", null=False)
    url = models.CharField("请求地址", null=False, max_length=200)
    method = models.CharField("请求方式", null=False, max_length=10)
    case = models.ForeignKey(Case, on_delete=models.CASCADE)
    step = models.IntegerField("顺序", null=False)


class HostIP(BaseTable):
    """
    全局变量
    """

    class Meta:
        verbose_name = "HOST配置"
        db_table = "HostIP"

    name = models.CharField(null=False, max_length=100)
    value = models.TextField(null=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)


class Variables(BaseTable):
    """
    全局变量
    """

    class Meta:
        verbose_name = "全局变量"
        db_table = "Variables"

    key = models.CharField(null=False, max_length=100)
    value = models.CharField(null=False, max_length=1024)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    description = models.CharField("全局变量描述", null=True, max_length=100)


class Report(BaseTable):
    """
    报告存储
    """
    report_type = (
        (1, "调试"),
        (2, "异步"),
        (3, "定时"),
        (4, "部署"),
    )

    class Meta:
        verbose_name = "测试报告"
        db_table = "Report"

    name = models.CharField("报告名称", null=False, max_length=100)
    type = models.IntegerField("报告类型", choices=report_type)
    summary = models.TextField("报告基础信息", null=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)


class ReportDetail(models.Model):
    class Meta:
        verbose_name = "测试报告详情"
        db_table = "ReportDetail"

    report = models.OneToOneField(Report, on_delete=models.CASCADE, null=True)
    summary_detail = models.TextField("报告详细信息")


class Relation(models.Model):
    """
    树形结构关系
    """

    class Meta:
        verbose_name = "树形结构关系"
        db_table = "Relation"

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    tree = models.TextField("结构主题", null=False, default=[])
    type = models.IntegerField("树类型", default=1)


[
    {
        "name": "testcase",
        "body": "body",
        "url": "https://www.baidu.com",
        "method": "post",
        "project": "1",
        "relation": 1
    }
]
