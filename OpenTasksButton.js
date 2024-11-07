
tasks_id = sessionStorage.getItem("tasks_id");

if (tasks_id == null) {
var xhr = new XMLHttpRequest();

xhr.open("GET", "https://apistore360.luxottica.com/svtapi/survey_task?visit_id=" + visit_id + "&survey_id=" + survey_id + "", false);
xhr.setRequestHeader("Authorization", "Basic UFJPRF9VU0VSOmQ4MG1aaCRh");

xhr.send(null);
if (xhr.status === 200) {
console.log(xhr);
  console.log(xhr.response);
  tasks_id = xhr.response.evalJSON().task_id;
}
sessionStorage.setItem("tasks_id", tasks_id);
}

function addPreviousTasks(qInfo) {
	var tasks = {};
	var t = 0;
	tasks_id.replace(/([^=,]+):([^,]*)/g, function ($0, param, value) {
	   	tasks[t] = {param,value};
	   	t++;
	});
//console.log("tasks");
//console.log(tasks);

	let button = $('open_task');
	let tKeys = Object.keys(tasks);
	let qKeys = Object.keys(qInfo);

	for (t = 0; t < tKeys.length; t++) {
//console.log("t: "+t);
//console.log("param: "+tasks[t].param);
//console.log(qInfo[tasks[t].param].QuestionText.trim());
//console.log(tasks[t].value);

		if(qKeys.includes(tasks[t].param)) {
			let newDiv = document.createElement("DIV");
			newDiv.style = "text-align: left;";
			newDiv.innerHTML = 'A Task was created for Question <STRONG>"' + htmlDecode(qInfo[tasks[t].param].QuestionText.trim()) + '"</STRONG>: task ID = ' + tasks[t].value;
			button.insertAdjacentElement("beforebegin", newDiv);
		}
 	}
}




function htmlDecode(input){
  var e = document.createElement('textarea');
  e.innerHTML = input.replace(/\n/g, '');
  // handle case of empty input
  return e.childNodes.length === 0 ? "" : e.childNodes[0].nodeValue;
}	
	
function createTaskQuestions(qid, qInfo) {
	let button = $('open_task');
        let d = document.getElementById('task_questions');
        if (d == null) {
        	d = document.createElement("SELECT");
			d.id = "task_questions";
            d.length = 0;
			d.style = "width: 100%; height: 2rem; margin-bottom: 2rem;";

			let defaultOption = document.createElement('option');
            defaultOption.text = 'Select a question to assign a task to';
            defaultOption.value = '';

            d.add(defaultOption);
            d.selectedIndex = 0;

            let option;
			
            let keys = Object.keys(Qualtrics.SurveyEngine.QuestionInfo);

	console.log("keys");
	console.log(keys);
			
			for (let i = 0; i < keys.length-1; i++) {
            	option = document.createElement('option');
                option.id = qid + "~" + option.value;
	console.log("option.id: " + option.id);
                option.value = qInfo[keys[i]].QuestionID;
	console.log("option.value: " + option.value);
                option.text = htmlDecode(qInfo[keys[i]].QuestionText).replace(/<\/?[^>]+(>|$)/g, "");
	console.log("option.text: " + option.text);
                d.add(option);
            }


            button.insertAdjacentElement("beforebegin", d);

        }
}

function openTask(button) {
  let d = document.getElementById('task_questions');
  let questionID;
  let options;
  if (!!d) {
     questionID = d.value;
     options = d.options;
  }
  if (questionID == "") {
    alert("Select a question from the list");
    return;
  }
  let body = '{';
  body += '"QID":"' + questionID + '",';
  body += '"response_id":"' + response_id + '",';
  body += '"survey_id":"' + survey_id + '",';
  body += '"survey_name":"' + survey_name + '",';
  body += '"user_id":"' + user_id + '",';
  body += '"visit_id":"' + visit_id + '"';
  body += '}';
  console.log("body: " + body);
  window.parent.postMessage(body, window.parent.location.origin);
  window.webkit.messageHandlers.svtCreateTaskHandler.postMessage(body);
}
