from models import Contributor, Contribution
from nr_comics.models import Comic
from nr_utils import render_with_request
from django.contrib.admin.views.decorators import staff_member_required
from django.db import connection
import collections

def contribution_list(request):
    """the contributions list page!!"""
    # {id: {id, sequence, title, date}}
    public_comics = {}
    for comic in Comic.comics.public().values('id','sequence','title','date'):
        public_comics[comic["id"]] = comic
    
    # {contribution_id: [{id, sequence, title, date}...]}
    cursor = connection.cursor()
    cursor.execute('SELECT contribution_id, comic_id from nr_comics_comic_origin')
    cc_relation = collections.defaultdict(list)
    for (con_id, comic_id) in cursor.fetchall():
	if comic_id in public_comics:
            cc_relation[con_id].append(public_comics[comic_id])

    tmap = {}
    for t in Contribution.CONTRIBUTION_TYPES:
        tmap[t[0]] = t[1]    
    def nice_type(contribution):
        contribution["contribution_type"] = tmap[contribution["contribution_type"]]
        return contribution
    public_contributions = map(nice_type,Contribution.objects.exclude(flagged=False).values())
        
    plural_contributions = []
    for contributor in Contributor.objects.exclude(id=666):
        contributions = []
        for con in public_contributions:
            if con['contributor_id'] == contributor.id and con['id'] in cc_relation:
                contributions.append({
                    "contribution": con,
                    "comics": cc_relation[con['id']]
                })
        if contributions:
            plural_contributions.append({
                "contributor": contributor,
                "contributions": contributions,
            })
    
    single_contributions = []
    for con in public_contributions:
        if con['contributor_id'] == 666 and con['id'] in cc_relation:
            single_contributions.append({
                "aka": con['aka'].lower(),
                "contribution": con,
                "comics": cc_relation[con['id']]
            })
    
    return render_with_request(
        "nr_contributions/list.html",
        {
            "plural": plural_contributions,
            "single": single_contributions,
        },
        request
    )

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.forms import ModelForm

class ContributionForm(ModelForm):
    class Meta:
        model = Contribution
        fields = ('aka', 'content')

from nr_contributions.signals import nr_contrib_added
def send_contribution_notification(contribution):
    nr_contrib_added.send(sender=Contribution,contribution=contribution)

def submit(request):
    if request.method == 'POST':
        form = ContributionForm(request.POST)
        if form.is_valid():
            send_contribution_notification(form.save())
            return HttpResponseRedirect('/contribute/thanks/')
    else:
        form = ContributionForm()
    return render_with_request('nr_contributions/submit.html',
                                      {'form':form}, request)

def submitjs(request):
    if request.method == 'POST':
        form = ContributionForm(request.POST)
        if form.is_valid():
            send_contribution_notification(form.save())
            return HttpResponse("<span class='thanks'>THANK YOU FOR YOUR SUGGESTION</span>")
    else:
        form = ContributionForm()
    return render_with_request('nr_contributions/jssubmit.html',{'form':form},request)
            

def thanks(request):
    return render_with_request('nr_contributions/thanks.html',{},request)

@staff_member_required
def report(request):
    """makes the unused suggestions report"""
    return render_with_request(
        'admin/nr_contributions/report.html',
        {
            'flagged': Contribution.objects.all().filter(flagged=True,contribution_type='suggested',comic=None).order_by("-submitted"),
            'unflagged': Contribution.objects.all().filter(flagged = False, contribution_type = 'suggested').order_by("-submitted"),
            'recent': Contribution.objects.all().filter(flagged=True,contribution_type='suggested').exclude(comic=None).order_by("-comic__date")[:30],
        },
        request
    )
