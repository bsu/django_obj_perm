from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase


from object_permissions import register, grant, revoke, get_user_perms, \
    get_model_perms, revoke_all, get_users, set_user_perms
from object_permissions.models import *
from object_permissions.signals import granted, revoked


class TestSignals(TestCase):
    
    def setUp(self):
        self.tearDown()
        
        self.granted = []
        self.revoked = []
        
        user = User(username='tester')
        user.save()
        group = UserGroup()
        group.save()
        object = Group(name='testgroup')
        object.save()
        
        register('Perm1', Group)
        register('Perm2', Group)
        register('Perm3', Group)
        
        granted.connect(self.granted_receiver)
        revoked.connect(self.revoked_receiver)
        
        g = globals()
        g['user'] = user
        g['group'] = group
        g['object_'] = object
    
    def tearDown(self):
        User.objects.all().delete()
        UserGroup.objects.all().delete()
        Group.objects.all().delete()
        ObjectPermission.objects.all().delete()
        GroupObjectPermission.objects.all().delete()
        ObjectPermissionType.objects.all().delete()
        
        granted.disconnect(self.granted_receiver)
        revoked.disconnect(self.revoked_receiver)
    
    def granted_receiver(self, sender, perm, object, **kwargs):
        """ receiver for callbacks """
        self.granted.append((sender, perm, object))
    
    def assertGranted(self, sender, perm, object):
        """ asserts that a signal was received """
        t = sender, perm, object
        if not t in self.granted:
            self.fail('Signal was not received: %s, %s, %s' % t)
    
    def revoked_receiver(self, sender, perm, object, **kwargs):
        """ receiver for callbacks """
        self.revoked.append((sender, perm, object))
    
    def assertRevoked(self, sender, perm, object):
        """ asserts that a signal was received """
        t = sender, perm, object
        if not t in self.revoked:
            self.fail('Signal was not received: %s, %s, %s' % t)
    
    def test_grant(self):
        user.grant('Perm1', object_)
        self.assertGranted(user, 'Perm1', object_)
    
    def test_revoke(self):
        user.revoke('Perm1', object_)
        self.assertRevoked(user, 'Perm1', object_)
    
    def test_grant_group(self):
        group.grant('Perm1', object_)
        self.assertGranted(group, 'Perm1', object_)
    
    def test_revoke_group(self):
        group.revoke('Perm1', object_)
        self.assertRevoked(group, 'Perm1', object_)
    
    def test_revoke_all(self):
        user.grant('Perm1', object_)
        user.grant('Perm2', object_)
        user.revoke_all(object_)
        self.assertRevoked(user, 'Perm1', object_)
        self.assertRevoked(user, 'Perm2', object_)
    
    def test_revoke_all_group(self):
        group.grant('Perm1', object_)
        group.grant('Perm2', object_)
        group.revoke_all(object_)
        self.assertRevoked(group, 'Perm1', object_)
        self.assertRevoked(group, 'Perm2', object_)
    
    def test_set_group_perms(self):
        user.grant('Perm1', object_)
        user.set_perms(['Perm2','Perm3'], object_)
        self.assertRevoked(user, 'Perm1', object_)
        self.assertGranted(user, 'Perm2', object_)
        self.assertGranted(user, 'Perm3', object_)
    
    def test_set_user_perms(self):
        group.grant('Perm1', object_)
        group.set_perms(['Perm2','Perm3'], object_)
        self.assertRevoked(group, 'Perm1', object_)
        self.assertGranted(group, 'Perm2', object_)
        self.assertGranted(group, 'Perm3', object_)