"""Check evidence and owner-only submission gates without inventing approvals."""
import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
OWNER_GATES = {
    'account_flow_verified': 'Test owner approval, rejected access, email sign-in, expiry and revocation.',
    'user_acceptance_recorded': 'Record designated-user expected and actual scenario results.',
    'training_effectiveness_recorded': 'Record unassisted operation and actual feedback.',
    'advisor_requirements_confirmed': 'Check the latest Blackboard prompts and rubric.',
    'team_authorship_reviewed': 'Confirm personal work and follow the course AI/authorship policy.',
    'deployment_choice_accepted': 'Verify the selected local or external deployment and handover.',
    'final_group_approval': 'All members review the actual final files before upload.',
}


def digest(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def advanced_fresh(report, root=ROOT):
    base = root/'backend/app/understanding'
    return all((base/name).is_file() and digest(base/name) == value
               for name, value in report.get('service_sha256', {}).items()) and bool(report.get('service_sha256'))


def owner_results(attestations):
    # An unfilled prompt, a string such as "true", or an omitted field is not
    # a signed-off outcome. The operator must retain the underlying evidence.
    return {key: {'complete': attestations.get(key) is True, 'next_action': action}
            for key, action in OWNER_GATES.items()}


def check(attestations=None, check_services=False):
    docs = ['INSTALL_ON_YOUR_COMPUTER.md','AWS_DEPLOYMENT.md','PASSWORDLESS_ACCESS.md',
            'SECURITY_GUARDRAILS.md','SECURITY_VERIFICATION.md','ACCURACY_UPGRADE.md',
            'MODELS_AND_DATA.md','FINAL_SUBMISSION_CHECKLIST.md','CODE_MAP.md']
    checks = {'documentation_present': all((ROOT/'docs'/name).is_file() for name in docs)}
    advanced = json.loads((ROOT/'docs/advanced-model-evaluation.json').read_bytes())
    checks['advanced_evidence_fresh'] = advanced_fresh(advanced)
    broad = json.loads((ROOT/'docs/broad-negation-after.json').read_bytes())
    checks['broad_evidence_fresh'] = all(digest(ROOT/path) == broad[key] for key, path in {
        'rules_sha256':'backend/app/nlp/negex_pipeline.py',
        'vocabulary_sha256':'backend/app/nlp/vocabulary.py',
        'ontology_sha256':'backend/app/data/disease_ontology_lexicon.json'}.items())
    ontology = json.loads((ROOT/'backend/app/data/disease_ontology_lexicon.json').read_bytes())
    summary = json.loads((ROOT/'frontend/src/data/terminologyEvidence.json').read_bytes())
    checks['terminology_provenance'] = (ontology['license']=='CC0-1.0'
        and bool(re.fullmatch(r'[a-f0-9]{40}',ontology['revision']))
        and summary['source_sha256']==ontology['source_sha256']
        and summary['unambiguous_terms']==len(ontology['entries'])
        and summary['ambiguous_terms']==len(ontology['ambiguous_entries'])
        and (ROOT/'backend/app/data/DISEASE_ONTOLOGY_LICENSE.txt').is_file())
    settings = {}
    env = ROOT/'backend/.env'
    if env.exists():
        for line in env.read_text(encoding='utf-8-sig').splitlines():
            if '=' in line and not line.lstrip().startswith('#'):
                key,value=line.split('=',1);settings[key.strip()]=value.strip()
    checks['owner_account_ids_configured'] = bool(settings.get('WORKOS_CLIENT_ID') and settings.get('WORKOS_ORGANIZATION_ID'))
    if check_services:
        try:
            with urlopen('http://localhost:8000/api/v1/health',timeout=10) as response:
                health=json.load(response)
            with urlopen('http://localhost:3000/preview',timeout=10) as response:
                frontend=response.status==200
            checks['local_services_ready'] = bool(health.get('qdrant_connected') and health.get('whisper_loaded') and frontend)
        except (OSError,ValueError):
            checks['local_services_ready'] = False
    owner = owner_results(attestations or {})
    return {'technical_checks':checks,'owner_checks':owner,
            'ready_for_final_submission':all(checks.values()) and all(row['complete'] for row in owner.values()),
            'medical_accuracy_98_validated':False,
            'note':'Software evidence and task scores do not constitute clinical validation. No secrets or personal journal text are included.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--attestations',type=Path)
    parser.add_argument('--services',action='store_true')
    parser.add_argument('--write-json',type=Path)
    args=parser.parse_args()
    attestations=json.loads(args.attestations.read_bytes()) if args.attestations else {}
    result=check(attestations,args.services)
    text=json.dumps(result,indent=2)+'\n'
    if args.write_json:args.write_json.parent.mkdir(parents=True,exist_ok=True);args.write_json.write_text(text,encoding='utf-8')
    print(text)
    raise SystemExit(0 if result['ready_for_final_submission'] else 2)
