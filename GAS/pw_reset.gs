function gaslog_formSubmit(e) {
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

  // https://next-k.site/blog/archives/2022/05/06/795
  let URL = PropertiesService.getScriptProperties().getProperty("API_ENDPOINT") + "/pw-reset";
  let data = {'user': userName };
  let headers = { 'Authorization': PropertiesService.getScriptProperties().getProperty("AUTH_VALUE") };
  let options = {
    "headers": headers,
    "Content-Type": "application/json",
    "method": "post",
    "payload": JSON.stringify(data)
  };

  UrlFetchApp.fetch(URL, options);
}
