function sendMailToAdmin(body) {
  // ex) 管理者にメールが届いていなければ、フォーム外から送られたことになる
  //    ADMIN_EMAILs = "asd@asd.com, qwe@qwe.com, zxc@zxc.com"
  // or ADMIN_EMAILs = "asd@asd.com"
  let emails = PropertiesService.getScriptProperties().getProperty('ADMIN_EMAILs');

  let subject = '[管理者用] パスワードリセット依頼を受け付けました'
  GmailApp.sendEmail(emails, subject, body);
}

function sendMailToRequester(body, email) {
  let subject = '[依頼者用] パスワードリセット依頼を受け付けました'
  GmailApp.sendEmail(email, subject, body);
}
