from flask import render_template, Blueprint, session, redirect, url_for
from CTFd.models import db, Solves
from sqlalchemy.sql import or_
from CTFd import utils
import json

from flask_sqlalchemy import get_debug_queries

from itsdangerous import Signer
from hashlib import sha256

PLUGIN_NAME = 'virtual-machine-plugin'

# Add a new class to the models
class VMs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    chalid = db.Column(db.Integer, db.ForeignKey('challenges.id'))
    desc = db.Column(db.Text)

    def __init__(self, name, chalid, desc):
        self.name = name
        self.chalid = chalid
        self.desc = desc

# Add new endpoint
def load(app):
    vm_pages = Blueprint('virtual_machines', __name__)
    db.create_all()

    # Clean and recreate the vm table for debugging 
    # XXX: Remove this 
    VMs.query.delete()
    db.session.add(VMs("Test Virtual Machine",1,"This is a test virtual machine for a challenge. To access, run `ssh user@128.213.48.144` the password is `user`"))
    db.session.commit()
    db.session.close()

    # Route for the VM page
    @vm_pages.route('/vm/', methods=['GET'])
    def virtual_machines_view():
        # Check if authed
        if not utils.authed() or not 'id' in session:
            return redirect(url_for('auth.login', next='vm'))

        # Look for all vms that the team has access too (has solved the chal)
        vmso = VMs.query.join(Solves, Solves.teamid == int(session['id'])).filter(Solves.chalid == VMs.chalid).all()

        vms = []
        # Set up the json data
        for v in vmso:
            signer = Signer(utils.get_config('VM_KEY'), salt=v.name, digest_method=sha256)
            vms.append({'name':v.name,
                'desc':v.desc,
                'key':signer.sign(json.dumps({'team':session['id'], 'vm':v.name})).encode('base64').replace('\n','')})
        
        # Run the template
        return render_template(PLUGIN_NAME+'/vms.html', vms=vms)

    app.register_blueprint(vm_pages)



