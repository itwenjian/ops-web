# -*- coding: utf-8 -*-
import json

from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user

from opsweb.auth.admin import is_cmdb_admin
from opsweb.cmdb import cmdb
from opsweb.dao.db_cmdb_kvm_project import DBCmdbKvmProject
from opsweb.dao.db_cmdb_kvm_virtual_server import DBCmdbKVMVirtualServer
from opsweb.dao.db_cmdb_physics_server_user import DBCmdbPhysicsServerUser
from opsweb.dao.db_cmdb_project import DBCmdbProject
from opsweb.dao.db_cmdb_user import *


@cmdb.route('/kvm/project/list', methods=['GET'])
@login_required
def cmdb_kvm_project_list():
    username = current_user.name
    server_projects = DBCmdbKvmProject.query.all()
    current_app.logger.info('%s visit cmdb-kvm-privilege-list page.', username)
    return render_template('cmdb_kvm_project_list.html', server_projects=server_projects)


@cmdb.route('/kvm/project/add', methods=['GET', 'POST'])
@login_required
@is_cmdb_admin
def cmdb_kvm_project_add():
    username = current_user.name
    if request.method == 'GET':
        servers = DBCmdbKVMVirtualServer.query.all()
        projects = DBCmdbProject.query.all()
        return render_template('cmdb_kvm_project_add.html', servers=servers, projects=projects)
    if request.method == 'POST':
        try:
            server_hostname = request.form['server_hostname']
            project_name = request.form['project_name']
            server = DBCmdbKVMVirtualServer.query.filter_by(hostname=server_hostname).first()
            project = DBCmdbProject.query.filter_by(name=project_name).first()
            server_privilege = DBCmdbKvmProject(server.id, server.hostname, project.id, project.name)
            db_cmdb.session.add(server_privilege)
            db_cmdb.session.commit()
        except Exception as error:
            db_cmdb.session.rollback()
            flash(current_app.config.get('DATA_EXIST'), 'alert')
            return redirect(request.referrer)
        return redirect(url_for("cmdb.cmdb_kvm_project_list"))
    return 'You should never reach here'


# todo
@cmdb.route('/kvm/project/edit', methods=['GET', 'POST'])
@login_required
def kvm_project_edit():
    username = current_user.name
    if request.method == 'GET':
        server_privilege_id = int(request.args.get('serverPrivilegeId', '0'))
        server_privilege = DBCmdbPhysicsServerUser.query.filter_by(id=server_privilege_id).first()
        return render_template('cmdb_kvm_project_edit.html', server_privilege=server_privilege)
    if request.method == 'POST':
        server_privilege_id = request.form['serverPrivilegeId']
        server_hostname = request.form['server_hostname']
        cmdb_user_name = request.form['cmdb_user_name']
        server = DBCmdbPhysicsServerUser.query.filter_by(hostname=server_hostname).first()
        cmdb_user = DBCmdbUser.query.filter_by(name=cmdb_user_name).first()

        server_privilege = DBCmdbPhysicsServerUser.query.filter_by(id=server_privilege_id).first()
        server_privilege.server_id = server.id
        server_privilege.server_hostname = server.hostname
        server_privilege.cmdb_user_id = cmdb_user.id
        server_privilege.cmdb_user_name = cmdb_user.name
        server_privilege.cmdb_user_cname = cmdb_user.cname
        db_cmdb.session.commit()
        return redirect(url_for("cmdb.cmdb_kvm_privilege_list"))
    return 'You should never reach here'


@cmdb.route('/kvm/project/del', methods=['GET'])
@login_required
@is_cmdb_admin
def cmdb_kvm_project_del():
    username = current_user.name
    server_privilege_id = int(request.args.get('serverPrivilegeId', '0'))

    server_privilege = DBCmdbKvmProject.query.filter_by(id=server_privilege_id).first()
    db_cmdb.session.delete(server_privilege)
    db_cmdb.session.commit()

    return redirect(url_for("cmdb.cmdb_kvm_project_list"))
