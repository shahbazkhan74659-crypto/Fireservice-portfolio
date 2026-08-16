from django.db import migrations

# Data-fix, same spirit as 0035_fix_hvws_mvws_service_name.py: 0037 already
# seeded these 10 blog posts against real dev/prod databases, so editing its
# RunPython body wouldn't retroactively fix the existing rows.
#
# Client direction: the business now positions itself as serving clients
# across India (main office in Silvassa), not a Silvassa/DNH-local operation.
# Only the "where we work" business-scope sentences below are reworded here
# — each post's title, excerpt, and the substantive regulatory content about
# the actual DNH & Daman & Diu Fire NOC notification/department (which is a
# real, jurisdiction-specific fact, not a service-area claim) are left
# untouched, matching the same distinction already applied to the site's
# templates this session.
REPLACEMENTS = [
    (
        'Fire NOC Renewal Deadline in Dadra & Nagar Haveli: What You Need to Know',
        'What we can tell you, from doing this work across Silvassa and the wider '
        'Vapi–Valsad–Umbergaon–Sarigam industrial belt, is that the businesses '
        'who come through this smoothly are the ones who treat the assessment, '
        'documentation and any system upgrades as one connected process, not '
        'three separate scrambles.',
        'What we can tell you, from doing this work across India, with our main '
        'office in Silvassa, is that the businesses who come through this '
        'smoothly are the ones who treat the assessment, documentation and any '
        'system upgrades as one connected process, not three separate scrambles.',
    ),
    (
        'Fire NOC Renewal Deadline in Dadra & Nagar Haveli: What You Need to Know',
        'Iconic Techno Service is ISO 9001:2015 and ISO 45001:2018 certified, and '
        'we work across Silvassa, Vapi, Valsad, Umbergaon and Sarigam helping '
        'businesses get — and stay — compliant.',
        'Iconic Techno Service is ISO 9001:2015 and ISO 45001:2018 certified, and '
        'we work across India, with our main office in Silvassa, helping '
        'businesses get — and stay — compliant.',
    ),
    (
        'Fire NOC in Dadra & Nagar Haveli: A Complete Guide for Business Owners',
        "That's the role we play for businesses across Silvassa, Vapi, Valsad, "
        "Umbergaon and Sarigam. We're ISO 9001:2015 and ISO 45001:2018 "
        'certified, and Fire NOC compliance work — assessment through to '
        'system installation — is a core part of what we do every week, not a '
        'side offering.',
        "That's the role we play for businesses across India, from our main "
        "office in Silvassa. We're ISO 9001:2015 and ISO 45001:2018 certified, "
        'and Fire NOC compliance work — assessment through to system '
        'installation — is a core part of what we do every week, not a side '
        'offering.',
    ),
    (
        'Provisional vs. Final Fire NOC: What’s the Difference and Why It Matters',
        'We help clients across Silvassa, Vapi, Valsad, Umbergaon and Sarigam '
        "prepare for both provisional and final Fire NOC stages — assessing "
        "what's actually in place against what's required, closing installation "
        'gaps, and making sure the documentation reflects real, working systems '
        'rather than paperwork alone.',
        'We help clients across India, from our main office in Silvassa, prepare '
        "for both provisional and final Fire NOC stages — assessing what's "
        "actually in place against what's required, closing installation gaps, "
        'and making sure the documentation reflects real, working systems '
        'rather than paperwork alone.',
    ),
    (
        'What Happens If Your Fire NOC Lapses in DNH?',
        'We help businesses across Silvassa, Vapi, Valsad, Umbergaon and Sarigam '
        'get a clear, honest picture of where they stand and what it would take '
        'to close any gap — including the on-site systems work, not just the '
        'paperwork.',
        'We help businesses across India, from our main office in Silvassa, get '
        'a clear, honest picture of where they stand and what it would take to '
        'close any gap — including the on-site systems work, not just the '
        'paperwork.',
    ),
    (
        'Fire Safety Compliance Checklist for Industrial Units in Silvassa and the Vapi-Valsad Corridor',
        'When we carry out a site survey for an industrial client — whether in '
        'Silvassa itself or across the Vapi, Valsad, Umbergaon or Sarigam GIDC '
        "estates — we're working through broadly the same set of areas every "
        'time.',
        'When we carry out a site survey for an industrial client anywhere in '
        "India, we're working through broadly the same set of areas every time.",
    ),
    (
        'Fire Safety Compliance Checklist for Industrial Units in Silvassa and the Vapi-Valsad Corridor',
        'We work across Silvassa and the wider '
        'Vapi–Valsad–Umbergaon–Sarigam industrial corridor, and '
        "we're ISO 9001:2015 and ISO 45001:2018 certified.",
        'We work across India, with our main office in Silvassa, and we\'re ISO '
        '9001:2015 and ISO 45001:2018 certified.',
    ),
    (
        'HVWS vs. MVWS: Water Spray Fire Protection for Transformers and Turbines',
        'Iconic Techno Service designs and installs HVWS and MVWS systems for '
        'transformer, turbine and high-hazard area protection across Silvassa, '
        'Vapi, Valsad and the wider DNH industrial corridor, alongside the '
        'detection systems that trigger them.',
        'Iconic Techno Service designs and installs HVWS and MVWS systems for '
        'transformer, turbine and high-hazard area protection across India, '
        'from our main office in Silvassa, alongside the detection systems '
        'that trigger them.',
    ),
    (
        'CO2 Gas Flooding vs. Clean Agent Suppression: Protecting Server Rooms and Sensitive Equipment',
        'We design and install CO2 gas flooding systems for server rooms, '
        'archives and other high-value, water-sensitive spaces across Silvassa '
        'and the wider DNH and South Gujarat industrial corridor, paired with '
        'the detection systems that make them effective.',
        'We design and install CO2 gas flooding systems for server rooms, '
        'archives and other high-value, water-sensitive spaces across India, '
        'from our main office in Silvassa, paired with the detection systems '
        'that make them effective.',
    ),
    (
        'Addressable vs. Conventional Fire Alarm Systems: Which Does Your Facility Need?',
        'Iconic Techno Service designs and installs both addressable and '
        'conventional fire detection systems for facilities across Silvassa, '
        'Vapi, Valsad, Umbergaon and Sarigam, using recognized OEM components '
        'and sizing the system to what your facility actually needs rather '
        'than a one-size answer.',
        'Iconic Techno Service designs and installs both addressable and '
        'conventional fire detection systems for facilities across India, '
        'from our main office in Silvassa, using recognized OEM components '
        'and sizing the system to what your facility actually needs rather '
        'than a one-size answer.',
    ),
    (
        'Fire Extinguisher Types Explained: A Hazard-Class Guide for Chemical and Industrial Plants',
        'We supply, install and service all types of fire extinguishers for '
        'chemical and industrial facilities across Silvassa, Vapi, Valsad, '
        "Umbergaon and Sarigam — including refilling and certification, so "
        "what's on your wall is actually ready when it's needed.",
        'We supply, install and service all types of fire extinguishers for '
        'chemical and industrial facilities across India, from our main '
        "office in Silvassa — including refilling and certification, so "
        "what's on your wall is actually ready when it's needed.",
    ),
    (
        'Essential Fire Safety Equipment for Industrial Units: PPE, SCBA, Signage and More',
        'Iconic Techno Service supplies safety equipment — PPE, SCBA sets, '
        'signage and more — for industrial and institutional facilities '
        'across Silvassa, Vapi, Valsad, Umbergaon and Sarigam, as part of a '
        'complete fire and life-safety package rather than a standalone '
        'product list.',
        'Iconic Techno Service supplies safety equipment — PPE, SCBA sets, '
        'signage and more — for industrial and institutional facilities '
        'across India, from our main office in Silvassa, as part of a '
        'complete fire and life-safety package rather than a standalone '
        'product list.',
    ),
]


def _apply(apps, schema_editor, forward):
    BlogPost = apps.get_model('website', 'BlogPost')
    for title, old, new in REPLACEMENTS:
        src, dst = (old, new) if forward else (new, old)
        try:
            post = BlogPost.objects.get(title=title)
        except BlogPost.DoesNotExist:
            continue
        if src in post.body:
            post.body = post.body.replace(src, dst)
            post.save(update_fields=['body'])


def generalize_service_area(apps, schema_editor):
    _apply(apps, schema_editor, forward=True)


def revert_service_area(apps, schema_editor):
    _apply(apps, schema_editor, forward=False)


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0054_delete_brand'),
    ]

    operations = [
        migrations.RunPython(generalize_service_area, revert_service_area),
    ]
