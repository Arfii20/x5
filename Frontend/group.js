const BASE = "http://127.0.0.1:5000/";
const logged_in_hrefs = document.querySelector(".if-logged-in");
const not_logged_in_hrefs = document.querySelector(".if-not-logged-in");
const hamburger = document.querySelector(".hamburger");

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

// const user_id = getCookie("user_id");
const user_id = 630;

if (user_id === null || user_id === undefined) {
  window.location.href = "../login.html";
}
not_logged_in_hrefs.style.display = "";
logged_in_hrefs.style.display = "none";
hamburger.style.display = "none";

async function postGroup(event){
	event.preventDefault();
	const CGbutton = event.target;

	const form = CGbutton.closest('form');
	const group_CGElement = form.querySelector('input[placeholder*="Group name"]');
	const group_CGPassElement = form.querySelector('input[placeholder*="Group password"]');
	const group_MaxuserElement = form.querySelector('input[placeholder*="Max users"]');


	const group_CG = group_CGElement.value;
	const group_CGPass = group_CGPassElement.value;
	const group_Maxuser = group_MaxuserElement.value;


	if (group_CG === "") {
		setInputError(group_CGElement, 'Please create Group Name');
		return;
	}
	else{
		clearInputError(group_CGElement);
	}


    if (group_CGPass === "") {
		setInputError(group_CGPassElement, 'Please create Group Password');
		return;
	}
	else{
		clearInputError(group_CGPassElement);
	}

    if (group_Maxuser === 0) {
        setInputError(group_MaxuserElement, 'Please enter max users');
        return;
    } else if (!Number.isInteger(Number(group_Maxuser)) || (Number(group_Maxuser) <= 0)) {
        setInputError(group_MaxuserElement, 'The number of users should be a positive integer');
        return;
    } else {
        clearInputError(group_MaxuserElement);
    }


	const response = await fetch(BASE + "house", {
												  	method: 'POST',
												  	headers: {
												    	'Content-Type': 'application/json'
												  	},
												  	body: JSON.stringify({
														user_id: null,
												    	first_name: register_Fname,
												    	surname: register_Lname,
														email: register_Email,
														password: register_Password,
														dob: register_Birth,
														household_id: null,
														colour: null,
												  	})
												})
  	if (response.ok) {
    	console.log({message: "House creation successful"});
    	const obj = await JSON.parse(await response.json());

    	setCookies(obj.u_id, obj.household, obj.email);
    	window.location.href = "./welcome.html";
  	} else {
    	throw new Error('Request failed.');
  	}
}



async function patchGroup(event){
	event.preventDefault();
    // console.log("sis");
	const JGbutton = event.target;

    const form = JGbutton.closest('form');
    const group_JGElement = form.querySelector('input[placeholder*="Group name"]');
    const group_JGPassElement = form.querySelector('input[placeholder*="Group password"]');

    const group_JG = group_JGElement.value;
    const group_JGPass = group_JGPassElement.value;

    if (group_JG === "") {
		setInputError(group_JGElement, 'Please enter Group Name');
		return;
	}
	else{
		clearInputError(group_JGElement);
	}

    if (group_JGPass === "") {
		setInputError(group_JGPassElement, 'Please enter Group Password');
		return;
	}
	else{
		clearInputError(group_JGPassElement);
	}






}

function setInputError(inputElement, errorMessage, inputGroupSelector = '.form__input-group') {
	const inputGroupElement = inputElement.closest(inputGroupSelector);
	const errorElement = inputGroupElement.querySelector('.form__input-error-message');
	inputGroupElement.classList.add('form__input-group--error');
	errorElement.innerText = errorMessage;
}

function clearInputError(inputElement, inputGroupSelector = '.form__input-group') {
	const inputGroupElement = inputElement.closest(inputGroupSelector);
	const errorElement = inputGroupElement.querySelector('.form__input-error-message');
	inputGroupElement.classList.remove('form__input-group--error');
	errorElement.innerText = '';
}

function setCookies(user_id, house_id, email_id) {
	// Get the current date
	const currentDate = new Date();

	// Add one day to the current date
	const tomorrowDate = new Date(currentDate);
	tomorrowDate.setDate(currentDate.getDate() + 2);

	// Set the time to 12:00:00
	tomorrowDate.setHours(12);
	tomorrowDate.setMinutes(0);
	tomorrowDate.setSeconds(0);
	tomorrowDate.setMilliseconds(0);

	// Convert the date to a UTC string
	const expires = tomorrowDate.toUTCString();

	// Set the path of the cookie
	const path = "/"; 

	// Set the cookie with a name, value, expiration date, and path
	document.cookie = "user_id=" + user_id + "; expires=" + expires + "; path=" + path;
	document.cookie = "house_id=" + house_id + "; expires=" + expires + "; path=" + path;
	document.cookie = "email_id=" + email_id + "; expires=" + expires + "; path=" + path;
}

function logout(){
	// Get all cookies and split them into an array
	const cookies = document.cookie.split(";");

	// Loop through all cookies and delete them by setting their expiration date to a date in the past
	for (let i = 0; i < cookies.length; i++) {
	    const cookie = cookies[i];
	    const eqPos = cookie.indexOf("=");
	    const name = eqPos > -1 ? cookie.substr(0, eqPos) : cookie;
	    document.cookie = name + "=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
	}

	console.log("Cookies cleared");

	window.location.href = "login.html";
}