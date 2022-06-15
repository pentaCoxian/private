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
    }else{
        gurl = `http://icu-syllabus.com/test_wsgi?${searchTerm}`;
    };
    fetch(gurl,{method:'GET'}).then(response => response.json()).then(data => insertFromJsonList(data));

    console.log(gurl);

}

function insertFromJsonList(jsonList){
    //input
    console.log(jsonList);

    //delete previous results
    let target = document.getElementsByClassName("result");
    for (let i = target.length -1;i >= 0;--i){
        target[i].remove();
    }

    let times = 0;
    for( i = 0; i <jsonList.length;i++){
        json1 = jsonList[i];
        markup = `
        <div class="result">
            <p>${json1.regno}</p>
            <p>${json1.score}</p>
            <p>${json1.sumlabel}</p>
            <div>${json1.results}</div>
        </div>
        `
       
        document.getElementById("target").insertAdjacentHTML("beforeend", markup);

        console.log(times);
        times ++;
    }
    console.log('exit');
}
