# client.views

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from django.core.context_processors import csrf

import mako
from mako.template import Template
from mako.lookup import TemplateLookup


mplates = TemplateLookup(directories=['client/templates/client'])

from api.models import *

def index(request):
    print Game
    print '----'
    print get_object_or_404(Game, pk=1)
    print '----'
    g = get_object_or_404(Game, pk=1)
    p = None

    session_pid = request.session.get('player_id')
    if session_pid:
        p = Player.objects.get(pk=session_pid)
    if not p and hasattr(request.user, 'playerconnector'):
        p = request.user.playerconnector.player

    return render(request, 'client/index.html', {
        'g': g,
        'p': p,
    })

def authorize(request, player_id, token):
    p = get_object_or_404(Player, pk=player_id)
    if p.authorize_new_session(token):
        request.session['player_id'] = p.id
        return HttpResponse('Logged in')
    else:
        request.session['player_id'] = None
        return HttpResponse('Wrong auth')

def player(request, player_id):
    session_pid = request.session.get('player_id')
    p = get_object_or_404(Player, pk=session_pid)
    return render(request, 'client/player.html', {
        'p': p,
    })

def charactor(request, charactor_id):
    session_pid = request.session.get('player_id')
    p = get_object_or_404(Player, pk=session_pid)
    results = [c for c in p.charactor_set.all()
               if c.id == int(charactor_id)]
    if not results:
        raise Http404("Charactor not found in Player %s's list" % session_pid)
    c = results[0]
    return makoify(request, 'charactor',
        c=c,
        g=c.game,
        MissionStunt=MissionStunt,
        start_allowed=c.game.start_allowed(c.player, on_fail=False),
    )

def charactor_submission(request, charactor_id, submission_id):
    session_pid = request.session.get('player_id')
    p = get_object_or_404(Player, pk=session_pid)
    results = [c for c in p.charactor_set.all()
               if c.id == int(charactor_id)]
    if not results:
        raise Http404("Charactor not found in Player %s's list" % session_pid)
    c = results[0]
    s = get_object_or_404(Submission, pk=submission_id)

    role = s.role_of_charactor(c)

    return makoify(request, 'charactor_submission',
        c=c,
        s=s,
        g=c.game,
        role=role,
    )

def make_url(name, *args, **kwargs):
    return reverse(name, args=args, kwargs=kwargs)

def make_csrf(request):
    return '<input type="hidden" name="csrfmiddlewaretoken" value="%s" />' %\
        csrf(request)["csrf_token"]

def makoify(request, template_prefix, **kw):
    template = mplates.get_template(template_prefix +'.mako')
    #print 'Template'
    #print template.filename
    #print template.source[:100]
    try:
        result = template.render(
            csrf=make_csrf(request),
            make_url=make_url,
            lookup=mplates,
            **kw
        )
    except:
        result = mako.exceptions.html_error_template().render()
    return HttpResponse(result)



