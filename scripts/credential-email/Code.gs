/** OmniMatch: one credential-request email per new WorkOS waitlist entry.
 * Google Apps Script V8. No public webhook and no automatic access approval.
 * Secrets belong in Script Properties, never in this file.
 */
const OWNER_DEFAULT = 'suhasreddykotla222@gmail.com';
const PORTAL_DEFAULT = 'https://omnimatch-research.onrender.com/login/';

function credentialTemplate(requestId, owner, portal) {
  return {
    subject: 'OmniMatch access request: please share your professional details [' + requestId + ']',
    body: [
      'Hello,', '',
      'Thank you for requesting access to OmniMatch. I review each request before approving access.', '',
      'Please reply to this email from the same address you used to request access and include:', '',
      '1. Your full name and professional designation or specialty.',
      '2. Your hospital, clinic or institution, and country of practice.',
      '3. Your medical registration or license number and the issuing authority.',
      '4. A link to your official professional registry record, if available. For U.S. providers, please include your NPI.',
      '5. Your institutional email or staff-directory link, if available.',
      '6. A contact phone number with country code, only if you would like me to contact you by phone (optional).', '',
      'Please do not send passwords, email codes, patient information, government identity documents or unredacted ID-card photos. If further evidence is needed, I will discuss a suitable way to provide it.', '',
      'I will review your details and may confirm them with the relevant registry or institution. Sending this information does not automatically approve access.', '',
      'Once approved, you can continue here: ' + portal,
      'OmniMatch currently uses synthetic patient data for academic research. No real patient information should be entered.', '',
      'I will use your reply only to review and follow up on this access request. It remains in my email inbox and is not used to train a model. You may ask me to delete your verification correspondence.', '',
      'If you did not request access, please ignore this message or reply to let me know. No further reminders are sent by this automation.', '',
      'Thank you,', 'Suhas Reddy Kotla', 'OmniMatch', owner,
      'Request reference: ' + requestId,
    ].join('\n'),
  };
}

function configuration_() {
  const props = PropertiesService.getScriptProperties();
  const key = props.getProperty('WORKOS_API_KEY') || '';
  const owner = (props.getProperty('OWNER_EMAIL') || OWNER_DEFAULT).trim();
  const portal = props.getProperty('PORTAL_URL') || PORTAL_DEFAULT;
  if (!key || !safeEmail_(owner) || !/^https:\/\/[a-z0-9.-]+(?::443)?(?:\/[^\s]*)?$/i.test(portal)) {
    throw new Error('Configure WORKOS_API_KEY, a valid OWNER_EMAIL and HTTPS PORTAL_URL in Script Properties.');
  }
  const sender = Session.getEffectiveUser().getEmail();
  if (!sender || sender.toLowerCase() !== owner.toLowerCase()) {
    throw new Error('Run this script from the owner email account.');
  }
  return {props: props, key: key, owner: owner, portal: portal};
}

function safeEmail_(email) {
  return typeof email === 'string' && email.length <= 254 && /^[A-Za-z0-9.!#$%&'*+\/=?^_`{|}~-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+$/.test(email);
}

function getWorkOS_(path, config) {
  const response = UrlFetchApp.fetch('https://api.workos.com' + path, {
    method: 'get', headers: {Authorization: 'Bearer ' + config.key},
    muteHttpExceptions: true, followRedirects: false, validateHttpsCertificates: true,
  });
  if (response.getResponseCode() !== 200) throw new Error('WorkOS lookup failed. No requests were approved. Check API key and waitlist settings.');
  const content = response.getContentText();
  if (content.length > 1000000) throw new Error('WorkOS response too large.');
  const result = JSON.parse(content);
  if (!Array.isArray(result.data)) throw new Error('Unexpected WorkOS response.');
  return result;
}

function waitlistId_(config) {
  let id = config.props.getProperty('WORKOS_WAITLIST_ID');
  if (!id) {
    const lists = getWorkOS_('/user_management/waitlists', config).data;
    if (lists.length !== 1) throw new Error('Set WORKOS_WAITLIST_ID explicitly; the environment must identify one waitlist.');
    id = lists[0].id;
    config.props.setProperty('WORKOS_WAITLIST_ID', id);
  }
  if (!/^waitlist_[A-Za-z0-9]+$/.test(id)) throw new Error('Invalid waitlist ID.');
  return id;
}

function pendingEntries_(config) {
  const id = waitlistId_(config);
  const entries = [];
  let after = '';
  for (let page = 0; page < 5; page++) {
    const result = getWorkOS_('/user_management/waitlists/' + id + '/entries?state=pending&limit=100&order=asc' + (after ? '&after=' + encodeURIComponent(after) : ''), config);
    result.data.forEach(function(entry) {
      if (!entry || typeof entry.id !== 'string' || !/^wl_user_[A-Za-z0-9]+$/.test(entry.id) ||
          !safeEmail_(entry.email) || entry.state !== 'pending' ||
          (entry.waitlist_id && entry.waitlist_id !== id) || !Number.isFinite(Date.parse(entry.created_at))) {
        throw new Error('Unexpected waitlist entry. No email batch was sent.');
      }
      entries.push(entry);
    });
    after = result.list_metadata && result.list_metadata.after;
    if (!after) return entries;
    if (typeof after !== 'string' || after.length > 256) throw new Error('Invalid pagination cursor.');
  }
  throw new Error('More than 500 pending entries. Review the workload before enabling this small-project automation.');
}

/** Run first. Does not send messages or create triggers; existing entries excluded. */
function initializeAutomation() {
  const config = configuration_();
  pendingEntries_(config); // Validate access before setting the start boundary.
  if (!config.props.getProperty('GO_LIVE_AT')) config.props.setProperty('GO_LIVE_AT', new Date().toISOString());
  if (!config.props.getProperty('SEND_ENABLED')) config.props.setProperty('SEND_ENABLED', 'false');
  return previewNewRequests();
}

function newEntries_(config) {
  const cutoff = Date.parse(config.props.getProperty('GO_LIVE_AT'));
  if (!Number.isFinite(cutoff)) throw new Error('Run initializeAutomation first.');
  return pendingEntries_(config).filter(function(entry) {
    const created = Date.parse(entry.created_at);
    return created >= cutoff && created <= Date.now() + 300000 && !config.props.getProperty('DELIVERY_' + entry.id);
  });
}

/** Counts only: does not expose applicant email addresses in execution logs. */
function previewNewRequests() {
  const config = configuration_();
  return {eligibleRequests: newEntries_(config).length, sendingEnabled: config.props.getProperty('SEND_ENABLED') === 'true'};
}

/** Sends the template only to the owner for review. No applicant is contacted. */
function sendTestToOwner() {
  const config = configuration_();
  if (MailApp.getRemainingDailyQuota() < 1) throw new Error('No email quota remains.');
  const mail = credentialTemplate('TEST-ONLY', config.owner, config.portal);
  MailApp.sendEmail({to: config.owner, subject: '[TEST] ' + mail.subject, body: mail.body, replyTo: config.owner, name: 'OmniMatch'});
}

/** Enable only after checking the owner test message and start date. */
function enableAutomation() {
  const config = configuration_();
  previewNewRequests();
  const existing = ScriptApp.getProjectTriggers().filter(function(t) {return t.getHandlerFunction() === 'pollWaitlist';});
  if (!existing.length) ScriptApp.newTrigger('pollWaitlist').timeBased().everyMinutes(5).create();
  config.props.setProperty('SEND_ENABLED', 'true');
}

function pauseAutomation() {
  PropertiesService.getScriptProperties().setProperty('SEND_ENABLED', 'false');
}

/** On ambiguous delivery failure, hold for owner review; never auto-resend. */
function pollWaitlist() {
  const lock = LockService.getScriptLock();
  if (!lock.tryLock(1000)) return;
  try {
    const config = configuration_();
    if (config.props.getProperty('SEND_ENABLED') !== 'true') return;
    const entries = newEntries_(config);
    const limit = Math.min(10, MailApp.getRemainingDailyQuota());
    for (let i = 0; i < Math.min(entries.length, limit); i++) {
      const entry = entries[i];
      const marker = 'DELIVERY_' + entry.id;
      // Record before sending: a crash must not cause an unsolicited duplicate.
      config.props.setProperty(marker, JSON.stringify({state: 'needs_review', at: new Date().toISOString()}));
      const mail = credentialTemplate(entry.id.slice(-12), config.owner, config.portal);
      try {
        MailApp.sendEmail({to: entry.email.trim().toLowerCase(), subject: mail.subject, body: mail.body, replyTo: config.owner, name: 'OmniMatch'});
        config.props.setProperty(marker, JSON.stringify({state: 'sent', at: new Date().toISOString()}));
      } catch (error) {
        // Do not include provider errors, credentials or applicant addresses.
        throw new Error('Email delivery outcome uncertain. Check Sent mail and DELIVERY_ markers before any manual resend.');
      }
    }
  } finally { lock.releaseLock(); }
}
