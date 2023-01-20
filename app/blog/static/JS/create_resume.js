// Flash query response function
function flash_response(message, status){
    // Flash response
    const flashed = document.getElementById("flashes")
    let flash = `<li>
        <div class="alert alert-${status}">
            ${message}
            <input type="button" class="alert-cancel dismiss" id="alert-cancel" value="X">
        </div>
    </li>
    `
    flashed.innerHTML = flash

    const buttons = document.getElementsByClassName("dismiss")

    for (let i=0; i < buttons.length; i++){
        let button = buttons[i]

        button.addEventListener("click",() => {
            button.parentElement.style.display = "none"
        })
    }
}


// Select Select Section On Display
function form_display(){
    let forms = document.getElementsByTagName("form")
    for (const form of forms){
        form.classList.add("remove_display")
    }

    const section_two = document.getElementsByClassName("section_two")
    for (const elem_child of section_two[0].children){
        elem_child.classList.add("remove_display")
    }

    // Education Records
    const education_records = document.querySelector(".education_record")
    education_records.classList.add("remove_display")

    // Companies Records
    const available_companies = document.getElementById("companies")
    available_companies.classList.add("remove_display")

    // Experiene Records
    const experience_records = document.querySelector(".experience_records")
    experience_records.classList.add("remove_display")
}

form_display()
const welcome = document.querySelectorAll(".welcome_content")
welcome.forEach((welcome_element) => {
    welcome_element.classList.remove("remove_display")
})

const section_name = document.getElementById("section_name")
section_name.addEventListener("change", () =>{
    form_display()
    const elements_in_view = document.querySelectorAll(`.${section_name.value}`)
    elements_in_view.forEach((element_in_view) => {
        element_in_view.classList.toggle("remove_display")
    })
})


// Resume Introduction Preview
const welcome_textarea = document.getElementById("welcome_textarea")
const preview_content_text = document.querySelector(".hero_content")
const welcome_save_btn = document.querySelector(".welcome_save_btn")

// Display Content In Preview Section
function preview_content(preview_content,welcome_textarea){
    preview_content.innerText = welcome_textarea.value
}

// Preview Event Listener
welcome_textarea.addEventListener("input",() => {
    preview_content(preview_content_text,welcome_textarea)
})

// Show current welcome text
preview_content(preview_content_text,welcome_textarea)

// Save Welcome Text
welcome_save_btn.addEventListener("click", (e) => {
    e.preventDefault()

    const form = new FormData()
    form.append("csrf_token", csrf_token.value)
    form.append("welcome_text", welcome_textarea.value)

    const xhr = new XMLHttpRequest()
    xhr.open("POST","/blog/update_welcome_text",true)
    xhr.send(form)

    xhr.onload = () => {
        const data = JSON.parse(xhr.responseText)
        const message = data["message"].toLowerCase()
        const status = data["status"].toLowerCase()

        // Show response
        flash_response(message,status)
    }
})


// About Section Preview
const about_textarea = document.getElementById("about_textarea")
const about_intro = document.querySelector(".about_intro")
const about_save_btn = document.querySelector(".about_save_btn")

// Preview Event Listener
about_textarea.addEventListener("input",() => {
    preview_content(about_intro,about_textarea)
})

// Show current welcome text
preview_content(about_intro,about_textarea)

// Save Welcome Text
about_save_btn.addEventListener("click", (e) => {
    e.preventDefault()

    const form = new FormData()
    form.append("csrf_token", csrf_token.value)
    form.append("about_text", about_textarea.value)

    const xhr = new XMLHttpRequest()
    xhr.open("POST","/blog/update_about_text",true)
    xhr.send(form)

    xhr.onload = () => {
        const data = JSON.parse(xhr.responseText)
        const message = data["message"].toLowerCase()
        const status = data["status"].toLowerCase()

        // Show response
        flash_response(message,status)
    }
})


// Work Section Preview
const work_textarea = document.getElementById("work_textarea")
const work_intro = document.querySelector(".work_intro")
const work_save_btn = document.querySelector(".work_save_btn")

// Preview Event Listener
work_textarea.addEventListener("input",() => {
    preview_content(work_intro,work_textarea)
})

// Show current welcome text
preview_content(work_intro,work_textarea)

// Save Welcome Text
work_save_btn.addEventListener("click", (e) => {
    e.preventDefault()

    const form = new FormData()
    form.append("csrf_token", csrf_token.value)
    form.append("work_text", work_textarea.value)

    const xhr = new XMLHttpRequest()
    xhr.open("POST","/blog/update_work_text",true)
    xhr.send(form)

    xhr.onload = () => {
        const data = JSON.parse(xhr.responseText)
        const message = data["message"].toLowerCase()
        const status = data["status"].toLowerCase()

        // Show response
        flash_response(message,status)
    }
})


// Education Section
const clear_form_btn = document.getElementById("clear_btn")
const name_fied = document.getElementById("Name")
const location_field = document.getElementById("Location")
const start_date_field = document.getElementById("Start_Date")
const End_date_field = document.getElementById("End_Date")
const Qualification = document.getElementById("Qualification")
const Save_btn = document.querySelector(".education_btn")
const Edit_btn = document.querySelector(".edit_btn")

// Clear Fields Data
function clear_form_fields(){
    name_fied.value = ""
    location_field.value = ""
    start_date_field.selectedIndex = 0;
    End_date_field.selectedIndex = 0;
    Qualification.value = ""

    Save_btn.classList.remove("remove_display")
    Edit_btn.classList.add("remove_display")
}

// Display Education Items
function display_education_items(item_list){
    const education_items = document.querySelector(".education_items")
    education_items.innerHTML = ""

    for(item of item_list){
        // Create Elements
        const education_item = document.createElement("div")
    
        const education_year = document.createElement("div")
        const year_paragraph = document.createElement("p")
    
        const education_instituition = document.createElement("div")
        const instituition_paragraph = document.createElement("p")
        const instituition_location = document.createElement("small")
    
        const award = document.createElement("div")
        
        // Create Qualifiation Element
        award.innerText = item["Qualification"]
        award.classList.add("education_award_name")

        // Create Instituition Element
        instituition_location.innerText = item["Location"]
        instituition_location.classList.add("education_location")
        instituition_paragraph.innerText = item["Instituition"]
        education_instituition.appendChild(instituition_paragraph)
        education_instituition.appendChild(instituition_location)
        education_instituition.classList.add("education_instituition")

        // Create Attendance Year Element
        year_paragraph.innerText = `${item["start_year"]} - ${item["end_year"]}`
        education_year.appendChild(year_paragraph)
        education_year.classList.add("education_year")

        // Create education element
        education_item.appendChild(education_year)
        education_item.appendChild(education_instituition)
        education_item.appendChild(award)

        education_items.appendChild(education_item)
    }
}

// Fetch Education Data
function fetch_education_records(){
    const new_promise = new Promise((resolve,reject) => {

        const xhr = new XMLHttpRequest()
        xhr.open("GET", "/blog/fetch_education_records", true)
        xhr.send()
        xhr.onload = () => {
            if (200 <= xhr.status && xhr.status < 300) {
                const data = JSON.parse(xhr.responseText)
                resolve(data)
            }
            else {
                reject("Unable to fetch saved records","failed")
            }
        }
    })
    .then((data) => {
        const status = data["status"].toLowerCase()

        // Show response
        if (status != "success"){
            const message = data["message"].toLowerCase()
            flash_response(message,status)
            return
        }

        // Clear Records List
        const edu_records = document.querySelector(".records_list")
        edu_records.innerHTML = ""

        // Create Elements
        const trash_element = document.createElement("div")
        const edit_element = document.createElement("div")

        trash_element.classList.add("trash_icon")
        trash_element.innerText = 'DELETE'

        edit_element.classList.add("edit_icon")
        edit_element.innerText = 'EDIT'

        // Display In Page
        for(const qualification of data["message"]["dict"]){
            const records_element = document.createElement("div")
            const qualification_element = document.createElement("div")

            records_element.classList.add("records")

            qualification_element.classList.add("credential")
            qualification_element.id = qualification["id"]
            qualification_element.innerText = qualification["Qualification"]

            const trash_element_clone = trash_element.cloneNode(true)
            const edit_element_clone = edit_element.cloneNode(true)

            // Add Event Listener to Edit Element
            edit_element_clone.addEventListener("click", () => {
                name_fied.value = qualification["Instituition"]
                location_field.value = qualification["Location"]
                Qualification.value = qualification["Qualification"]
                start_date_field.value = qualification["start_year"]
                End_date_field.value = qualification["end_year"]
            
                Save_btn.classList.add("remove_display")
                Edit_btn.classList.remove("remove_display")
                Edit_btn.id = qualification["id"]
            })

            // Add Event Listener To Trash Element
            trash_element_clone.addEventListener("click", () => {
                new Promise((resolve) => {
                    const record_id = qualification["id"]
                    const xhr = new XMLHttpRequest()
                    const form = new FormData()
    
                    form.append("csrf_token", csrf_token.value)
                    form.append("record_id",record_id)
    
                    xhr.open("POST","/blog/remove_education",true)
                    xhr.send(form)
                    xhr.onload = () => {
                        const data = JSON.parse(xhr.responseText)
                        const message = data["message"].toLowerCase()
                        const status = data["status"].toLowerCase()
                
                        // Show response
                        flash_response(message,status)
                    }
                    resolve()
                })

                .then(() => {
                    // Refresh Eduation Records
                    fetch_education_records()
                })
            })

            records_element.appendChild(qualification_element)
            records_element.appendChild(trash_element_clone)
            records_element.appendChild(edit_element_clone)

            edu_records.appendChild(records_element);
        }

        display_education_items(data["message"]["dict"])
    })
    .catch((message,status) => {
        flash_response(message,status)
    })
}

// Show Education Records
fetch_education_records()

// Clear Education Form Field
clear_form_btn.addEventListener("click", (e) => {
    e.preventDefault()
    clear_form_fields()
})


Save_btn.addEventListener("click", (e) => {
    e.preventDefault()

    new Promise((resolve) => {
        const form = new FormData()
        form.append("csrf_token", csrf_token.value)
        form.append("name", name_fied.value)
        form.append("location", location_field.value)
        form.append("start_date", start_date_field.value)
        form.append("end_date", End_date_field.value)
        form.append("qualification", Qualification.value)
    
        const xhr = new XMLHttpRequest()
        xhr.open("POST","/blog/add_education",true)
        xhr.send(form)
    
        xhr.onload = () => {
            const data = JSON.parse(xhr.responseText)
            const message = data["message"].toLowerCase()
            const status = data["status"].toLowerCase()
    
            // Show response
            flash_response(message,status)
        }
        resolve()
    })
    .then(() => {
        // Clear Form Fields
        clear_form_btn.click()
        
        // Refresh Saved Education data preview
        fetch_education_records()
    })
})

Edit_btn.addEventListener("click",(e) => {
    e.preventDefault()

    new Promise((resolve) => {
        const qualifiation_id = Edit_btn.id
        const form = new FormData()
    
        form.append("csrf_token", csrf_token.value)
        form.append("record_id", qualifiation_id)
        form.append("name", name_fied.value)
        form.append("location", location_field.value)
        form.append("start_date", start_date_field.value)
        form.append("end_date", End_date_field.value)
        form.append("qualification", Qualification.value)
    
        const xhr = new XMLHttpRequest()
        xhr.open("POST","/blog/update_education",true)
        xhr.send(form)
    
        xhr.onload = () => {
            const data = JSON.parse(xhr.responseText)
            const message = data["message"].toLowerCase()
            const status = data["status"].toLowerCase()
    
            // Show response
            flash_response(message,status)
        }
        resolve()
    })
    .then(() => {
        // Clear Form Fields
        clear_form_btn.click()

        // Refresh Saved Education data preview
        fetch_education_records()
    })
})


// Refresh Available companies
function refresh_available_companies(){
    const available_companies = document.querySelector(".available_companies")
    available_companies.innerHTML = ""
    let color_types = ["blue","green","red"]

    const xhr = new XMLHttpRequest()
    xhr.open("GET","/blog/fetch_companies",true)
    xhr.send()
    xhr.onload = () =>{
        const data = JSON.parse(xhr.responseText)
    
        for (const company of data["message"]["dict"]){
            const a = document.createElement("a")
            const content_div = document.createElement("div")
            const remove_div = document.createElement("div")
            const random_color = color_types[Math.floor(Math.random() * color_types.length)];

            remove_div.innerText = 'x'
            remove_div.classList.add("remove_icon")
            remove_div.id = `${company["company_uuid"]}`

            remove_div.addEventListener("click",() => {

                const form = new FormData()
                form.append("csrf_token",csrf_token.value)
                form.append("company_id",`${company["company_uuid"]}`)

                const remove_xhr = new XMLHttpRequest()
                remove_xhr.open("POST","/blog/remove_company",true)
                remove_xhr.send(form)

                remove_xhr.onload = () => {
                    const data = JSON.parse(remove_xhr.responseText)
                    const message = data["message"].toLowerCase()
                    const status = data["status"].toLowerCase()
            
                    // Show response
                    flash_response(message,status)
                }
                refresh_available_companies()
            })

            a.innerText = company["company_name"]
            a.setAttribute("href",`${company["company_url"]}`)

            content_div.appendChild(a)
            content_div.appendChild(remove_div)
    
            content_div.classList.add("company",`${random_color}`)
            available_companies.appendChild(content_div)
        }
    }
}
refresh_available_companies()

// Add Company Section
const add_company_btn = document.getElementById("add_company_btn")
add_company_btn.addEventListener("click", (e) => {
    e.preventDefault()

    const company_name = document.getElementById("company_name")
    const company_url = document.getElementById("company_url")

    new Promise((resolve) => {
        const form = new FormData
        form.append("csrf_token", csrf_token.value)
        form.append("company_name", company_name.value)
        form.append("company_url", company_url.value)

        const xhr = new XMLHttpRequest()
        xhr.open("POST","/blog/add_company",true)
        xhr.send(form)

        xhr.onload = () => {
            const data = JSON.parse(xhr.responseText)
            const message = data["message"].toLowerCase()
            const status = data["status"].toLowerCase()
    
            // Show response
            flash_response(message,status)
        }
        resolve()
    })
    .then(() => {
        refresh_available_companies()
    })
})


// Clear Experience Form
function clear_experience_form(){
    const company_name = document.getElementById("CompanyName")
    const company_role = document.getElementById("Role")
    const company_role_description = document.getElementById("Role_description")
    const start_month = document.getElementById("Start_Month")
    const start_year = document.getElementById("Start_Year")
    const end_month = document.getElementById("End_Month")
    const end_year = document.getElementById("End_Year")
    const save_btn = document.getElementById("save_experience_btn")
    const edit_options = document.querySelector(".edit_options")

    edit_options.classList.add("remove_display")
    save_btn.classList.remove("remove_display")

    company_name.selectedIndex = 0
    company_role.value = ""
    company_role_description.value = ""
    start_month.selectedIndex = 0
    start_year.selectedIndex = 0
    end_month.selectedIndex = 0
    end_year.selectedIndex = 0
}

// Update Experience Display Section
function update_experience_display(){
    const experience_records = document.querySelector(".experience_records")
    experience_records.innerHTML = ""

    // Fetch List Of Experience 
    const exp_xhr = new XMLHttpRequest()
    exp_xhr.open("GET","/blog/fetch_experience",true)
    exp_xhr.send()

    exp_xhr.onload = () => {
        const data = JSON.parse(exp_xhr.responseText)
        const status = data["status"].toLowerCase()
        const message = data["message"]

        if (status != "success"){
            flash_response(message, status)
            return
        }
        else{
    
            for (const company in message){
                for (const experience of message[company]){
                    const experience_record = document.createElement("div")
                    const experience_company_name = document.createElement("div")
                    const experience_role = document.createElement("div")
                    const experience_delete = document.createElement("div")
                    const experience_edit = document.createElement("div")

                    // delete Experience
                    experience_delete.innerText = "DELETE"
                    experience_delete.addEventListener("click",() => {
                        const form = new FormData()
                        form.append("csrf_token",csrf_token.value)
                        form.append("experience_id", experience["id"])
                        
                        const xhr = new XMLHttpRequest()
                        xhr.open("POST","/blog/delete_experience",true)
                        xhr.send(form)
                        xhr.onload = () => {
                            const data = JSON.parse(xhr.responseText)
                            const message = data["message"]
                            const status = data["status"]

                            flash_response(message,status)
                            load_experience_preview()
                        }
                    })

                    // Edit Experience
                    experience_edit.innerText = "EDIT"
                    experience_edit.addEventListener("click", () => {
                        const company_name = document.getElementById("CompanyName")
                        const company_role = document.getElementById("Role")
                        const company_role_description = document.getElementById("Role_description")
                        const start_month = document.getElementById("Start_Month")
                        const start_year = document.getElementById("Start_Year")
                        const end_month = document.getElementById("End_Month")
                        const end_year = document.getElementById("End_Year")
                        const save_btn = document.getElementById("save_experience_btn")
                        const edit_options = document.querySelector(".edit_options")
                        const edit_btn = document.querySelector(".edit_experience_btn")

                        save_btn.classList.add("remove_display")
                        edit_options.classList.remove("remove_display")
                        edit_btn.id = experience["id"]

                        company_name.value = experience["company_name"].toUpperCase()
                        company_role.value = experience["role_name"]
                        company_role_description.value = experience["role_description"]
                        
                        const edit_start_year = new Date(experience["start_year"])
                        start_month.value = `${edit_start_year.getMonth() + 1}`
                        start_year.value = edit_start_year.getFullYear()
                        
                        const edit_end_year = new Date(experience["end_year"])
                        end_month.value = `${edit_end_year.getMonth() + 1}`
                        end_year.value = edit_end_year.getFullYear()
                    })

                    experience_role.innerText = experience["role_name"]
                    experience_company_name.innerText = experience["company_name"]

                    experience_record.appendChild(experience_company_name)
                    experience_record.appendChild(experience_role)
                    experience_record.appendChild(experience_delete)
                    experience_record.appendChild(experience_edit)

                    experience_record.classList.add("experience_record")
                    experience_company_name.classList.add("experience_company_name")
                    experience_role.classList.add("experience_role")
                    experience_delete.classList.add("experience_delete")
                    experience_edit.classList.add("experience_edit")

                    experience_records.appendChild(experience_record)
                }
            }
        }
    }
}

// Display Experience Preview
function load_experience_preview(){
    const about_experience = document.querySelector(".about_experience")
    const experience_items = document.querySelector(".experience_items")
    experience_items.innerHTML = ""

    new Promise((resolve, reject) => {

        const exp_xhr = new XMLHttpRequest()
        exp_xhr.open("GET","/blog/fetch_experience",true)
        exp_xhr.send()

        exp_xhr.onload = () => {
            let months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
            const data = JSON.parse(exp_xhr.responseText)
            const message = data["message"]
            const status = data["status"].toLowerCase()

            if(status == "success"){
                // Update Preview Display
                for(const company in message){
                    // Create Company Experience Header
                    const experience_item = document.createElement("div")
                    const experience_company = document.createElement("div")
                    const experience_item_p = document.createElement("p")
                    const experience_company_positions = document.createElement("div")

                    experience_item.classList.add("experience_item")
                    experience_company.classList.add("experience_company")
                    experience_item_p.classList.add("_company")

                    experience_item_p.innerText = company
                    experience_company.appendChild(experience_item_p)
                    experience_item.appendChild(experience_company)

                    // Add Individual Company Experience
                    for (const experience of message[company]){
                        const company_position = document.createElement("div")
                        const position_year = document.createElement("div")
                        const position_name = document.createElement("div")
                        const position_description = document.createElement("div")

                        experience_company_positions.classList.add("experience_company_positions")
                        company_position.classList.add("company_position")
                        position_year.classList.add("position_year")
                        position_name.classList.add("position_name")
                        position_description.classList.add("position_description")

                        position_description.innerText = experience["role_description"]
                        position_name.innerText = experience["role_name"]

                        const experience_start_date = new Date(experience["start_year"])
                        const experience_end_date = new Date(experience["end_year"])

                        const exp_start_month = months[experience_start_date.getMonth()]
                        const exp_start_year = experience_start_date.getFullYear()
                        const exp_end_month = months[experience_end_date.getMonth()]
                        const exp_end_year = experience_end_date.getFullYear()
                        position_year.innerText =  `${exp_start_month}, ${exp_start_year} - ${exp_end_month}, ${exp_end_year}`

                        company_position.appendChild(position_year)
                        company_position.appendChild(position_name)
                        company_position.appendChild(position_description)

                        experience_company_positions.appendChild(company_position)
                        experience_item.appendChild(experience_company_positions)
                    }

                    experience_items.appendChild(experience_item)
                }

                update_experience_display()
            }
        }
    })
    about_experience.appendChild(experience_items)
}
load_experience_preview()


// Experience Section
const save_experience_btn = document.getElementById("save_experience_btn")
save_experience_btn.addEventListener("click", (e) => {
    e.preventDefault()

    new Promise((resolve) => {
        const company_name = document.getElementById("CompanyName")
        const role = document.getElementById("Role")
        const role_desc = document.getElementById("Role_description")
        const start_month = document.getElementById("Start_Month")
        const start_year = document.getElementById("Start_Year")
        const end_month = document.getElementById("End_Month")
        const end_year = document.getElementById("End_Year")
    
        const form = new FormData()
        form.append("csrf_token", csrf_token.value)
        form.append("company_name",company_name.value)
        form.append("role",role.value)
        form.append("role_description",role_desc.value)
        form.append("start_month",start_month.value)
        form.append("start_year",start_year.value)
        form.append("end_month", end_month.value)
        form.append("end_year", end_year.value)
    
        const xhr = new XMLHttpRequest()
        xhr.open("POST","/blog/add_experience",true)
        xhr.send(form)
        xhr.onload = () =>{
            const data = JSON.parse(xhr.responseText)
            const message = data["message"]
            const status = data["status"]
    
            flash_response(message, status)
        }
        resolve("success")
    })
    .then((status) => {
        if (status == "success"){
            load_experience_preview()
            clear_experience_form()
        }
    })
})


// Clear Experience Form
const experience_clear_btn = document.querySelector(".clear_experience_btn")
experience_clear_btn.addEventListener("click", (e) => {
    e.preventDefault()
    clear_experience_form()
}) 


// Edit Experience Form
const experience_edit_btn = document.querySelector(".edit_experience_btn")
experience_edit_btn.addEventListener("click", (e) => {
    e.preventDefault()

    new Promise((resolve) => {
        const company_name = document.getElementById("CompanyName")
        const role = document.getElementById("Role")
        const role_desc = document.getElementById("Role_description")
        const start_month = document.getElementById("Start_Month")
        const start_year = document.getElementById("Start_Year")
        const end_month = document.getElementById("End_Month")
        const end_year = document.getElementById("End_Year")
    
        const form = new FormData()
        form.append("csrf_token", csrf_token.value)
        form.append("company_name",company_name.value)
        form.append("role",role.value)
        form.append("role_description",role_desc.value)
        form.append("start_month",start_month.value)
        form.append("start_year",start_year.value)
        form.append("end_month", end_month.value)
        form.append("end_year", end_year.value)
        form.append("experience_id", experience_edit_btn.id)
    
        const xhr = new XMLHttpRequest()
        xhr.open("POST","/blog/update_experience",true)
        xhr.send(form)
        xhr.onload = () =>{
            const data = JSON.parse(xhr.responseText)
            const message = data["message"]
            const status = data["status"]
    
            flash_response(message, status)
        }
        resolve("success")
    })
    .then((status) => {
        if (status == "success"){
            load_experience_preview()
            clear_experience_form()
        }
    })
})