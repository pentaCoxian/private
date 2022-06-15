window.onload = function(){
    let searchButton = document.getElementById("searchButton");
    searchButton.addEventListener('click',()=>{searchFunc();});
}
// a
function searchFunc(e){
    console.log("fired");
    let searchTerm = document.getElementById("search").value.trim().replace(" ","+");
    let gurl = ''
    if (document.getElementById("switch").checked === true){
        gurl = `http://icu-syllabus.com/devpython-sub?${searchTerm}`;
        fetch(gurl,{method:'GET'}).then(response => response.json()).then(data => insertFromJsonListSub(data));
    }else{
        gurl = `http://icu-syllabus.com/devpython?${searchTerm}`;
        fetch(gurl,{method:'GET'}).then(response => response.json()).then(data => insertFromJsonList(data));
    };
    console.log(gurl);
}

function insertFromJsonList(jsonList){
    let target = document.getElementsByClassName("result");
    for (let i = target.length -1;i >= 0;--i){
        target[i].remove();
    }
    for( i = 0; i <jsonList.length;i++){
        json = jsonList[i];
        let markup = `
        <div class="result">
                <div class="result-main">
                    <div class="title">${json.course_no}: ${json.title_j} / ${json.title_e} (${json.lang})</div>
                    <div class="details">
                        <div class="regID">Reg: ${json.rgno}</div>
                        <div class="ay">AY: ${json.ay}/${(json.season)[0]}</div>
                        <div class="teacher">${json.instructor}</div>
                        <div class="flex-break"></div>
                        <div class="schedule">Schedule: ${json.schedule} [${json.room}, ${json.comment}]</div>
                        <div class="comment"></div>
                        <div class="units">Units: ${json.unit}</div>
                    </div>
                </div>
            </div>
        `;
        document.getElementById("target").insertAdjacentHTML("beforeend", markup);
    }
}

function insertFromJsonListSub(jsonList){
    //delete previous results
    let target = document.getElementsByClassName("result");
    for (let i = target.length -1;i >= 0;--i){
        target[i].remove();
    }

    for( i = 0; i <jsonList.length;i++){
        json1 = jsonList[i];
        
        markup = `
        <div class="result">
            <p>${json1.regno}</p>
            <div>${json1.results.join('')}</div>
            <p>----------------------------</p>
        </div>
        
        `
        document.getElementById("target").insertAdjacentHTML("beforeend", markup);
    }
}

function getIdAndNameRelation(){

}