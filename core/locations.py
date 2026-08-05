LOCATIONS = [
    {
        'slug': 'fire-safety-company-vapi',
        'town': 'Vapi',
        'title': 'Fire Safety Company in Vapi | Iconic Techno Service',
        'meta_description': 'Fire detection, suppression, extinguishers and AMC for industrial units in Vapi GIDC — ISO 9001 & 45001 certified, serving the Silvassa-Vapi corridor.',
        'h1': 'Fire Safety Systems & Compliance Services in Vapi',
        'intro': 'Vapi’s GIDC industrial estate sits roughly 20–30 minutes from our Silvassa office, and it’s one of the largest concentrations of manufacturing and chemical-processing units in the Silvassa–Vapi–Valsad corridor — which also means it carries real fire risk exposure, from solvent storage to high-load electrical infrastructure. We design, supply, install and maintain fire detection, suppression, extinguisher and pump house systems for facilities across Vapi GIDC, alongside Fire NOC compliance support under the current DNH & Daman & Diu enforcement notification.',
    },
    {
        'slug': 'fire-safety-systems-valsad-gidc',
        'town': 'Valsad GIDC',
        'title': 'Fire Safety Systems for Valsad GIDC | Iconic Techno Service',
        'meta_description': 'ISO 9001 & 45001 certified fire safety systems for industrial units in Valsad GIDC — detection, suppression, extinguishers, AMC and Fire NOC support.',
        'h1': 'Fire Safety Systems for Valsad GIDC Industrial Units',
        'intro': 'Valsad GIDC’s industrial units — spanning manufacturing, chemical processing and general engineering — fall within the same DNH & Daman & Diu fire safety enforcement notification affecting neighbouring Silvassa, and the same practical need for properly designed detection, suppression and extinguisher coverage. We serve Valsad GIDC facilities directly from our Silvassa office, covering everything from initial site assessment through installation, AMC and Fire NOC compliance support.',
    },
    {
        'slug': 'fire-safety-company-umbergaon',
        'town': 'Umbergaon',
        'title': 'Fire Safety Company Serving Umbergaon | Iconic Techno Service',
        'meta_description': 'Fire detection, suppression and extinguisher systems for industrial units in Umbergaon — ISO 9001 & 45001 certified, AMC and Fire NOC support included.',
        'h1': 'Fire Safety Company Serving Umbergaon Industrial Estate',
        'intro': 'Umbergaon’s industrial estate sits at the southern edge of the Silvassa–Vapi–Valsad corridor, with a mix of manufacturing and processing units that need the same properly-specified fire detection, suppression and extinguisher coverage as facilities closer to Silvassa itself. We support Umbergaon businesses with system design, installation, AMC and Fire NOC compliance guidance, coordinated from our Silvassa office.',
    },
    {
        'slug': 'fire-safety-company-sarigam',
        'town': 'Sarigam',
        'title': 'Fire Safety Company Serving Sarigam GIDC | Iconic Techno Service',
        'meta_description': 'Fire safety systems for industrial units in Sarigam GIDC — detection, suppression, extinguishers, AMC and Fire NOC compliance support. ISO 9001 & 45001 certified.',
        'h1': 'Fire Safety Company Serving Sarigam GIDC',
        'intro': 'Sarigam GIDC’s industrial units — chemical, pharmaceutical and general manufacturing among them — carry fire risk profiles that need properly matched detection and suppression, not a one-size response. We work with Sarigam facilities on system design, installation, AMC and Fire NOC compliance support, serving the area from our Silvassa office as part of the wider Silvassa–Vapi–Valsad–Umbergaon–Sarigam corridor we cover.',
    },
]


def get_location(slug):
    return next((loc for loc in LOCATIONS if loc['slug'] == slug), None)
