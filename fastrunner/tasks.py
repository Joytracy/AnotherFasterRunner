import datetime

from celery import shared_task, Task
from django_celery_beat.models import PeriodicTask
from django.core.exceptions import ObjectDoesNotExist
from fastrunner import models
from fastrunner.utils.loader import save_summary, debug_suite, debug_api
from fastrunner.utils.ding_message import DingMessage
from fastrunner.utils import lark_message


def update_task_total_run_count(task_id):
    if task_id:
        task = PeriodicTask.objects.get(id=task_id)
        total_run_count = task.total_run_count + 1
        dt = task.date_changed
        PeriodicTask.objects.filter(id=task_id).update(
            date_changed=dt, total_run_count=total_run_count
        )


class MyBaseTask(Task):
    def run(self, *args, **kwargs):
        pass

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        update_task_total_run_count(kwargs.get("task_id"))

    def on_success(self, retval, task_id, args, kwargs):
        update_task_total_run_count(kwargs.get("task_id"))


@shared_task
def async_debug_api(api, project, name, config=None):
    """异步执行api"""
    summary = debug_api(api, project, config=config, save=False)
    save_summary(name, summary, project)


@shared_task
def async_debug_suite(suite, project, obj, report, config, user=""):
    """异步执行suite"""
    summary, _ = debug_suite(suite, project, obj, config=config, save=False)
    save_summary(report, summary, project, user)


@shared_task(base=MyBaseTask)
def schedule_debug_suite(*args, **kwargs):
    """定时任务"""

    project = kwargs["project"]
    suite = []
    test_sets = []
    config_list = []
    for pk in args:
        try:
            name = models.Case.objects.get(id=pk).name
            suite.append({"name": name, "id": pk})
        except ObjectDoesNotExist:
            pass
    override_config = kwargs.get("config", "")
    override_config_body = None
    if override_config and override_config != "请选择":
        override_config_body = eval(
            models.Config.objects.get(name=override_config, project__id=project).body
        )

    for content in suite:
        test_list = (
            models.CaseStep.objects.filter(case__id=content["id"])
            .order_by("step")
            .values("body")
        )

        testcase_list = []
        config = None
        for content in test_list:
            body = eval(content["body"])
            if "base_url" in body["request"].keys():
                if override_config_body:
                    config = override_config_body
                    continue
                config = eval(
                    models.Config.objects.get(
                        name=body["name"], project__id=project
                    ).body
                )
                continue
            testcase_list.append(body)
        config_list.append(config)
        test_sets.append(testcase_list)

    is_parallel = kwargs.get("is_parallel", False)
    summary, _ = debug_suite(
        test_sets, project, suite, config_list, save=False, allow_parallel=is_parallel
    )
    task_name = kwargs["task_name"]

    if kwargs.get("run_type") == "deploy":
        task_name = "部署_" + task_name
        report_type = 4
    else:
        report_type = 3

    report_id = save_summary(
        task_name, summary, project, type=report_type, user=kwargs.get("user", "")
    )

    strategy = kwargs["strategy"]
    if strategy == "始终发送" or (strategy == "仅失败发送" and summary["stat"]["failures"] > 0):
        # ding_message = DingMessage(run_type)
        # ding_message.send_ding_msg(summary, report_name=task_name)
        webhook = kwargs.get("webhook", "")
        if webhook:
            summary["task_name"] = task_name
            summary["report_id"] = report_id
            lark_message.send_message(
                summary=summary, webhook=webhook, case_count=len(args)
            )
