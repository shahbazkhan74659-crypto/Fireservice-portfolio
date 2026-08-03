from django.db import migrations

# One-time seed: these titles/taglines previously lived as hardcoded <h3>/
# <p class="phase__tagline"> copy in process.html. Matched by `order`, same
# 1-7 positional convention 0023_seed_process_phases.py and
# 0025_seed_process_phase_cards.py used.
TITLES = {
    1: ('Initial Inquiry & Technical Risk Assessment', 'Customer Inquiry to On-Site Survey'),
    2: ('Design Engineering & Commercial Proposal', 'Calculations, Modeling & Budgeting'),
    3: ('Code Approvals & Regulatory Permitting', 'AHJ & Civil Defence Submission'),
    4: ('Procurement, Quality Assurance & Off-Site Prep', 'Material Sourcing & Fabrication'),
    5: ('Site Installation & MEP Integration', 'Execution & Physical Civil/Electrical Work'),
    6: ('Testing, Commissioning (T&C) & Inspection', 'Hydrostatic, Cause-and-Effect & Final AHJ Sign-Off'),
    7: ('Handover, Training & Ongoing AMC', 'As-Built Documentation & Preventive Maintenance'),
}


def seed_titles(apps, schema_editor):
    ProcessPhase = apps.get_model('website', 'ProcessPhase')
    for order, (title, tagline) in TITLES.items():
        ProcessPhase.objects.filter(order=order).update(title=title, tagline=tagline)


def unseed_titles(apps, schema_editor):
    ProcessPhase = apps.get_model('website', 'ProcessPhase')
    ProcessPhase.objects.filter(order__in=TITLES.keys()).update(title='', tagline='')


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0026_processphase_tagline_processphase_title'),
    ]

    operations = [
        migrations.RunPython(seed_titles, unseed_titles),
    ]
