const toggle = document.getElementById("theme-toggle");

// Page load hote hi theme apply karo
if(localStorage.getItem("theme") === "dark"){
    document.body.classList.add("dark");
    if(toggle){
        toggle.innerHTML="☀";
    }
}

if(toggle){

toggle.addEventListener("click",()=>{

document.body.classList.toggle("dark");

if(document.body.classList.contains("dark")){

localStorage.setItem("theme","dark");

toggle.innerHTML="☀";

}
else{

localStorage.setItem("theme","light");

toggle.innerHTML="🌙";

}

});

}