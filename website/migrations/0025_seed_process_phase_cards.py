from django.db import migrations

# One-time seed: these two explanation cards per phase previously lived as
# hardcoded copy in process.html (phase__card blocks). This migration copies
# that text onto the matching ProcessPhase row (matched by `order`, the same
# 1-7 positional convention 0023_seed_process_phases.py seeded the photos
# with) so the Admin Hub can edit them without touching template code.
CARDS = {
    1: (
        'Inquiry & Site Survey',
        'Every inquiry is logged with building type, hazard classification and timeline, then verified on-site — field engineers assess dimensions, water pressure/flow, electrical infrastructure and fire load.',
        'Hazard Classification',
        'Occupancy hazard level is classified under applicable codes (NFPA 13/14/72, NBC, local Civil Defence standards) to determine the right system design approach.',
    ),
    2: (
        'Engineering & Design',
        'Pipe sizing (Hazen-Williams) and voltage-drop calculations feed into 2D/3D CAD-BIM layouts, routing sprinklers, detectors and panels while coordinating with MEP and structural teams.',
        'Costing & Proposal',
        'A detailed Bill of Quantities covers piping, valves, pumps, detectors, panels and labor — submitted as a techno-commercial proposal for client sign-off.',
    ),
    3: (
        'Documentation & Submission',
        'Shop drawings, riser diagrams, cause-and-effect matrix and equipment datasheets are compiled and formally submitted to local authorities for permit review.',
        'Approval & Revisions',
        'Reviewer feedback is incorporated into the drawing set and resubmitted until final permit approval is secured.',
    ),
    4: (
        'Procurement & Testing',
        'UL-listed / FM-approved components — pumps, panels, sprinklers, clean-agent cylinders, detectors — are ordered, with critical equipment like main fire pumps factory-tested before dispatch.',
        'Off-Site Pre-fabrication',
        'Header pipes, grooved pipe spools and structural supports are cut and prepared off-site in advance to accelerate on-site installation.',
    ),
    5: (
        'Mechanical & Electrical Installation',
        'Fire mains, risers, zone valves, sprinkler drops and hose cabinets go in alongside fire alarm panels, addressable detectors, call points and voice evacuation systems.',
        'MEP Interlocking',
        'Systems are integrated with building services — HVAC trip-signals, stairwell pressurization, elevator recall, door release and access-control override — for coordinated emergency response.',
    ),
    6: (
        'Pressure & System Testing',
        'Piping is pressure-tested (typically 200 psi for 2 hours per NFPA) for leaks, then real fire scenarios are simulated to confirm detection, HVAC shutdown, agent release and pump start-up all trigger correctly.',
        'Final Inspection & Certification',
        'Civil Defence / Fire Department officials inspect the site, witness live tests and issue the Fire Safety Completion Certificate or Occupancy Permit.',
    ),
    7: (
        'Handover & Training',
        'As-built drawings, O&M manuals, warranty certificates and test reports are handed over, and facility staff are trained on panel operation, resets, manual releases and basic troubleshooting.',
        'Ongoing AMC',
        'Transition into scheduled quarterly, bi-annual and annual maintenance checks to keep the system compliant and audit-ready year-round.',
    ),
}


def seed_cards(apps, schema_editor):
    ProcessPhase = apps.get_model('website', 'ProcessPhase')
    for order, (card1_title, card1_text, card2_title, card2_text) in CARDS.items():
        ProcessPhase.objects.filter(order=order).update(
            card1_title=card1_title,
            card1_text=card1_text,
            card2_title=card2_title,
            card2_text=card2_text,
        )


def unseed_cards(apps, schema_editor):
    ProcessPhase = apps.get_model('website', 'ProcessPhase')
    ProcessPhase.objects.filter(order__in=CARDS.keys()).update(
        card1_title='', card1_text='', card2_title='', card2_text='',
    )


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0024_processphase_card1_text_processphase_card1_title_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_cards, unseed_cards),
    ]
