from django.shortcuts import render
from server.models import RemoteUserBindHost
from .models import TerminalLog, TerminalSession
from util.tool import login_required, post_required, admin_required
from django.http import JsonResponse
from django.db.models import Q
from .forms import HostForm, HostViewForm
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
# Create your views here.


@login_required
def hosts(request):
    if request.session['issuperuser']:
        hosts = RemoteUserBindHost.objects.all()
    else:
        hosts = RemoteUserBindHost.objects.filter(
            Q(user__username=request.session['username']) | Q(group__user__username=request.session['username'])
        ).distinct()
    return render(request, 'webssh/hosts.html', locals())


@login_required
@post_required
def terminal(request):
    host_form = HostForm(request.POST)
    error_message = '请检查填写的内容!'
    if host_form.is_valid():
        host_id = host_form.cleaned_data.get('hostid')
        host = RemoteUserBindHost.objects.get(id=host_id)
        return render(request, 'webssh/terminal.html', locals())

    return JsonResponse({"code": 406, "err": error_message})


@login_required
@admin_required
def logs(request):
    logs = TerminalLog.objects.all()
    return render(request, 'webssh/logs.html', locals())


@login_required
@admin_required
def sessions(request):
    sessions = TerminalSession.objects.all()
    return render(request, 'webssh/sessions.html', locals())


@login_required
@post_required
def terminal_view(request):
    hostview_form = HostViewForm(request.POST)
    error_message = '请检查填写的内容!'
    if hostview_form.is_valid():
        name = hostview_form.cleaned_data.get('sessionname')
        group = hostview_form.cleaned_data.get('group')
        session = TerminalSession.objects.get(name=name, group=group)
        return render(request, 'webssh/terminal_view.html', locals())

    return JsonResponse({"code": 406, "err": error_message})


# 每次重启时清空在线会话表
def cls_terminalsession():
    try:
        TerminalSession.objects.all().delete()
    except:
        pass
    

cls_terminalsession()