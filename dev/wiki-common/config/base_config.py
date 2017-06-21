import time
import os.path
from MoinMoin import user, log
from MoinMoin.auth import GivenAuth
from MoinMoin.web.session import FileSessionService
from MoinMoin.config.multiconfig import DefaultConfig


class SSLAuth(GivenAuth):

    # Usage:
    #auth = [SSLAuth()]

    def __init__(self):
        GivenAuth.__init__(self, env_var="HTTP_X_FORWARDED_USER")
        self.log = log.getLogger(__name__)

    def transform_username(self, name):
        return name[4:]

    def request(self, request, user_obj, **kw):
        u = None
        _ = request.getText

        # always revalidate auth
        if user_obj and user_obj.auth_method == self.name:
            user_obj = None

        # something else authenticated before us
        if user_obj:
            self.log.debug("already authenticated, doing nothing")
            return user_obj, True

        if self.user_name is not None:
            auth_username = self.user_name
        elif self.env_var is None:
            auth_username = request.remote_user
        else:
            auth_username = request.environ.get(self.env_var)

        self.log.debug("auth_username = %r" % auth_username)
        if auth_username:
            auth_username = self.decode_username(auth_username)
            auth_username = self.transform_username(auth_username)
            self.log.debug("auth_username (after decode/transform) = %r"
                    % auth_username)

        uid = user._getUserIdByKey(request, 'aliasname', auth_username)
        if uid is not None:
                u = user.User(request, uid, auth_method=self.name,
                        auth_attribs=('name', 'password'))

        self.log.debug("u: %r" % u)
        if u and self.autocreate:
            self.log.debug("autocreating user")
            u.create_or_update()

        if u and u.valid:
            self.log.debug("returning valid user %r" % u)
            return u, True # True to get other methods called, too
        else:
            self.log.debug("returning %r" % user_obj)
            return user_obj, True


class AuditingSessionService(FileSessionService):

    def finalize(self, request, session):
        if session.new:
            session["from_ua"] = request.in_headers.get("User-Agent")
            session["from_ip"] = request.in_headers.get("X-Forwarded-For")
            session["started"] = int(time.time())

        if not request.cfg.can_remember:
            request.user.remember_me = False

        FileSessionService.finalize(self, request, session)


class BaseConfig(DefaultConfig):

    data_dir = "/srv/wiki/data/" # Docker Default
    data_underlay_dir = os.path.join(data_dir, "underlay")

    page_front_page = u"FrontPage"

    # The default theme anonymous or new users get
    theme_default = u"levine_modernized"
    supplementation_page = True

    # The return address, e.g u"Jurgen Wiki <noreply@mywiki.org>" [Unicode]
    mail_from = u"wiki-noreply@levine.us"
    mail_sendmail = "/usr/sbin/sendmail -t -i"
    # SMTP server, e.g. "mail.provider.com" (None to disable mail)
    mail_smarthost = "localhost"

    acl_rights_before = u"AdminGroup:read,write,delete,revert,admin"
    acl_rights_after = u"All:"
    acl_rights_default = u"Known:read,write,delete,revert All:"
    acl_hierarchic = True

    actions_excluded = DefaultConfig.actions_excluded[:]
    actions_excluded.remove('xmlrpc')
    #actions_excluded.append('newaccount')

    logo_string = u'<img src="/WikiStatic?action=AttachFile&do=get&target=logo.png"/>'
    url_prefix_static = u"/static"

    # Add your wikis important pages at the end. It is not recommended to
    # remove the default links.  Leave room for user links - don't use
    # more than 6 short items.
    # You MUST use Unicode strings here, but you need not use localized
    # page names for system and help pages, those will be used automatically
    # according to the user selected language. [Unicode]
    navi_bar = [
        u'%(page_front_page)s',
        u'RecentChanges',
        u'FindPage',
        u'HelpContents'
    ]

    #cookie_secure = True
    cookie_httponly = True
    session_service = AuditingSessionService()
    can_remember = True

    # Moin won't use these if the proper bindings aren't installed
    xapian_search = True
    xapian_stemming = True

    superuser = [u"EricLevine", ]

    sitename = u'Development Wiki of HouseLevine'

     # The main wiki language, set the direction of the wiki pages
    language_default = 'en'

    # e.g. CategoryFoo -> group 'all' ==  CategoryFoo, group 'key' == Foo
    # moin's code will add ^ / $ at beginning / end when needed
    # You must use Unicode strings here [Unicode]
    page_category_regex = ur'(?P<all>Category(?P<key>(?!Template)\S+))'
    page_dict_regex = ur'(?P<all>(?P<key>\S+)Dict)'
    page_group_regex = ur'(?P<all>(?P<key>\S+)Group)'
    page_template_regex = ur'(?P<all>(?P<key>\S+)Template)'
