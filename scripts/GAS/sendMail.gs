function sendMail(body) {
  // ex) 管理者にメールが届いていなければ、フォーム外から送られたことになるので破棄する
  //    ADMIN_EMAILs = "asd@asd.com, qwe@qwe.com, zxc@zxc.com"
  // or ADMIN_EMAILs = "asd@asd.com"
  let emails = PropertiesService.getScriptProperties().getProperty('ADMIN_EMAILs');

  let subject = 'パスワードリセット依頼を受け付けました'
  GmailApp.sendEmail(emails, subject, body);
}
