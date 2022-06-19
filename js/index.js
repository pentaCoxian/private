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
        gurl = `https://icu-syllabus.com/devpython-sub?${searchTerm}`;
        //backup DDNS gurl = `http://pentacoxian.com/devpython-sub?${searchTerm}`;
        fetch(gurl,{method:'GET'}).then(response => response.json()).then(data => insertFromJsonListSub(data));
    }else{
        gurl = `https://icu-syllabus.com/devpython?${searchTerm}`;
        //backup DDNS gurl = `http://pentacoxian.com/devpython?${searchTerm}`;
        fetch(gurl,{method:'GET'}).then(response => response.json()).then(data => insertFromJsonList(data));
    };
    console.log(gurl);
}

function insertFromJsonList(jsonList){
    // delete previous results
    // loop through the elements from the back since the returned list is a live list and will get updated as you delete elements, resulting in a index number mismatch
    let target = document.getElementsByClassName("result");
    for (let i = target.length -1;i >= 0;--i){
        target[i].remove();
    }

    // insert html elements with the values from the recived json
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
        // use insertAdjacentHTML so that the script does not loose track of the DOM
        // if you use insert inside a loop, it will result in loss of DOM status and the script won't run after that
        document.getElementById("target").insertAdjacentHTML("beforeend", markup);
    }
}

function insertFromJsonListSub(jsonList){
    //delete previous results
    let target = document.getElementsByClassName("result");
    for (let i = target.length -1;i >= 0;--i){
        target[i].remove();
    }
    console.log()
    for( i = 0; i <jsonList.length;i++){
        json1 = jsonList[i];
        markup = `
        <div class="result">
            <div class="syWrapper">
                <div class="syRegno">Reg:${json1.regno}</div>
                <div class="syHeadder">${json1.course_no}: ${json1.title_e} / ${json1.title_j}</div>
            </div>

            <div>${json1.results.join('\n')}</div>
            <div class="sySeparator">----------------------------</div>
        </div>
        
        `
        document.getElementById("target").insertAdjacentHTML("beforeend", markup);
    }
}

function getIdAndNameRelation(){

}