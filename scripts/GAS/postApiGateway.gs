/*
プロジェクトの設定で、以下の環境変数を設定する
API_ENDPOINT: API GatewayのURL → https://{api_id}.execute-api.ap-northeast-1.amazonaws.com
AUTH_VALUE: Lambdaで検証するためのトークン
*/
function postApiGateway(e) {
  let email = e.response.getRespondentEmail();
  let itemResponses;
  // フォームの回答をイベントオブジェクトまたはフォーム自身から取得する。
  if (e !== undefined) {
    itemResponses = e.response.getItemResponses();
  } else {
    const wFormRes = FormApp.getActiveForm().getResponses();
    itemResponses =  wFormRes[wFormRes.length-1].getItemResponses();
  }
  // 取得したフォーム項目を1件ずつ処理する
  let userName = "";
  itemResponses.forEach(function(itemResponse){
    if (itemResponse.getItem().getTitle() == "ユーザー名") {
      userName = itemResponse.getResponse();
    }
  });

  let token = generateRandomString(32);
  let password = 'Pw0+' + generateRandomString(12);
  let data = {'user': userName, 'email': email, 'gform_token': token, 'tmp_password': password };
  let mailBodyToRequester = `
管理者の承認後、以下の情報でログインし、パスワードを再設定してください
ユーザー名: ${userName}
password: ${password}
※このメールが送られた時点ではログインできません
`
  sendMailToRequester(mailBodyToRequester, email);
  mailBodyToAdmin = `
後からslackに届く内容と一致することを確認してください
ユーザー名: ${userName}
email: ${email}
token: ${token}
`
  sendMailToAdmin(mailBodyToAdmin);
  let URL = PropertiesService.getScriptProperties().getProperty("API_ENDPOINT") + "/slack-workflow";
  Logger.log(data)
  let headers = { 'Authorization': PropertiesService.getScriptProperties().getProperty("AUTH_VALUE") };
  let options = {
    "headers": headers,
    "Content-Type": "application/json",
    "method": "post",
    // "muteHttpExceptions": true,
    "payload": JSON.stringify(data)
  };

  UrlFetchApp.fetch(URL, options);
}

function generateRandomString(length) {
  const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  const charactersLength = characters.length;
  for (let i = 0; i < length; i++) {
    result += characters.charAt(Math.floor(Math.random() * charactersLength));
  }
  return result;
}
