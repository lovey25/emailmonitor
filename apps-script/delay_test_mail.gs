// Google Apps Script: send one delay-test mail every five minutes, Mon-Fri 06:00-20:00 KST.
// Setup: Services → add "Gmail API"; Script property COMPANY_EMAIL = recipient; run install() once.
// Uses the Gmail API (not GmailApp/MailApp) to stay off the 100 recipients/day Apps Script quota.

const BODY = '자동으로 발송되는 테스트';

function sendDelayTest() {
  const now = new Date();
  const weekday = Number(Utilities.formatDate(now, 'Asia/Seoul', 'u')); // 1=Mon … 7=Sun
  const hhmm = Number(Utilities.formatDate(now, 'Asia/Seoul', 'HHmm'));
  // Triggers fire at a random offset inside each 5-minute slot, so allow the 20:00 slot.
  if (weekday > 5 || hhmm < 600 || hhmm >= 2005) return;
  send('[DELAY TEST]', now);
}

// Run manually any time to check the setup; ignores the weekday/time window.
function sendManualTest() {
  send('[MANUAL TEST]', new Date());
}

function send(prefix, now) {
  const to = PropertiesService.getScriptProperties().getProperty('COMPANY_EMAIL');
  const subject = `${prefix} ${Utilities.formatDate(now, 'Asia/Seoul', 'yyyy-MM-dd HH:mm:ss')}`;
  const raw = [
    `To: ${to}`,
    `Subject: ${subject}`,
    'Content-Type: text/plain; charset=UTF-8',
    'Content-Transfer-Encoding: base64',
    '',
    Utilities.base64Encode(BODY, Utilities.Charset.UTF_8),
  ].join('\r\n');
  Gmail.Users.Messages.send({ raw: Utilities.base64EncodeWebSafe(raw) }, 'me');
}

function install() {
  ScriptApp.getProjectTriggers().forEach((t) => ScriptApp.deleteTrigger(t));
  ScriptApp.newTrigger('sendDelayTest').timeBased().everyMinutes(5).create();
}
