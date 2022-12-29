// Generate random string function
function random(length = 16){
    return Math.random().toString(16).substr(2, length);
};

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

// Upload file function
function uploadFile(file) {

    const approved_category = ["audio","video","images"]

    // File Info
    const fileName = file.name;
    let fileSize = file.size;
    let fileType = file.type;

    // Check for valid files
    let file_category = fileType.split('/')[0]
    if (approved_category.includes(file_category)){

        //  File Name Data
        var fileExtension = fileName.split('.').pop();
        var random_name = random(16)
        var new_file_name = random_name + '.' + fileExtension;

        // Get File Size In MB or KB
        if (fileSize > 1000000) {
            fileSize = (fileSize / (1024 * 1024)).toFixed(2) + ' MB';
        } else {
            fileSize = (fileSize / 1024).toFixed(2) + ' KB';
        }

        // Create File Data from Form Data
        const fileData = new FormData();
        fileData.append('csrf_token', csrf_token.value)
        fileData.append('file', file);
        fileData.append('type',fileType)
        fileData.append('fileName', new_file_name);

        // Upload File
        let  xhr = new XMLHttpRequest();
        xhr.open('POST', '/blog/file_upload',true);

        // Update Progress Bar
        let uploader = xhr.upload

        // Uploader Upload
        uploader.addEventListener('progress', (e) => {
            const percentage = Math.round((e.loaded / e.total) * 100);

            let progressHTML =   `<p>Uploading...</p>`;
            
            upload_field.innerHTML = progressHTML;
        });

        // Send Request
        xhr.send(fileData);

        // On Request Complete
        xhr.onload = () => {
            console.log(xhr.responseText)
            const data = JSON.parse(xhr.responseText)
            const message = data["message"].toLowerCase()
            const status = data["status"].toLowerCase()

            // Remove Progress Bar
            upload_field.innerHTML = `<p>Upload Files</p>`;

            // Show response
            flash_response(message,status)
        }
        
    }

}

// Disble Input element
function disable_element(element){
    element.disabled = true
}

// Enable Input Element
function enable_element(element) {
    element.disabled = false
}

// remove html element display
function remove_display(element){
    element.classList.add("remove_display")
}

// enable html element display
function fix_display(element){
    element.classList.remove("remove_display")
}

// Get All Post Types
const post_types = document.querySelectorAll(".post_type")

// Enable Post Type and Suitable attachment files
post_types.forEach((post_type) => {
    post_type.addEventListener("click", () => {
        post_types.forEach((post_typ) => {
            post_typ.classList.remove("select")
        })
        post_type.classList.add("select")
        post_text = post_type.innerText

        if (post_text.toLowerCase() == "plain post"){
            disable_element(file_upload)
            
            audio_files.forEach((audio_file) => {
                remove_display(audio_file)
            })

            image_files.forEach((image_file) => {
                remove_display(image_file)
            })

            video_files.forEach((video_file) => {
                remove_display(video_file)
            })
        }

        if (post_text.toLowerCase() == "audio post"){
            enable_element(file_upload)

            audio_files.forEach((audio_file) => {
                fix_display(audio_file)
            })

            image_files.forEach((image_file) => {
                remove_display(image_file)
            }) 
            
            video_files.forEach((video_file) => {
                remove_display(video_file)
            })
        }

        if (post_text.toLowerCase() == "image post" | post_text.toLowerCase() == "images post"){
            enable_element(file_upload)

            audio_files.forEach((audio_file) => {
                remove_display(audio_file)
            })

            image_files.forEach((image_file) => {
                fix_display(image_file)
            }) 
            
            video_files.forEach((video_file) => {
                remove_display(video_file)
            })
        }

        if (post_text.toLowerCase() == "video post"){
            enable_element(file_upload)

            audio_files.forEach((audio_file) => {
                remove_display(audio_file)
            })

            image_files.forEach((image_file) => {
                remove_display(image_file)
            }) 
            
            video_files.forEach((video_file) => {
                fix_display(video_file)
            })
        }


    })
})

// Select article category
let article_checkbox = document.getElementById("outer_selector")
let article_checkbox_marker = document.getElementById("inner_selector")
let new_category = document.getElementById("new_category")
let available_categories = document.getElementById("available_categories")

article_checkbox.addEventListener('click',() => {
    article_checkbox_marker.classList.toggle("remove_display")
    new_category.classList.toggle("remove_display")
    available_categories.classList.toggle("remove_display")
})

// Article search


// Show article viewing
const articles = document.querySelectorAll(".article")

articles.forEach((article) => {
    article.addEventListener("click", () => {
        articles.forEach((post) => {
            post.classList.remove("viewing")
        })
        article.classList.add("viewing")

        // set post type

        // add update button display
        remove_display(publish_article)
        fix_display(update_article)

        // Display in article create section
    })
})

// buttons
const new_article = document.getElementById("new")
const draft_article = document.getElementById("draft")
const publish_article = document.getElementById("publish")
const update_article = document.getElementById("update")
const preview_article = document.getElementById("preview")


// Create New Article interface
new_article.addEventListener('click', () => {

    const article_title = document.getElementById("content_header")
    const article_body = document.getElementById("content")

    remove_display(update_article)
    fix_display(publish_article)

    article_title.value = ""
    article_body.value = ""

    articles.forEach((article) => {
        article.classList.remove("viewing")
    })
})

// Save to draft
draft_article.addEventListener('click',() => {
    const article_title = document.getElementById("content_header")
    const article_body = document.getElementById("content")
    const post_type = document.querySelectorAll(".select")
    const blogger_id = document.getElementById("blogger_id")
    let post_text = post_type.innerText
    let category = null

    // artcle category
    if ("remove_display" in article_checkbox_marker.classList){
        category = document.getElementById("select_field").value
    }
    else{
        category = document.getElementById("category_name").value
    }

    if (category == ""){
        flash_response("Category not set","warning")
        return
    }

    const articleData = new FormData();
    articleData.append('csrf_token', csrf_token.value)
    articleData.append('title', article_title);
    articleData.append('body',article_body)
    articleData.append("post_type",post_text)
    articleData.append("category",category)
    articleData.append("author_uid", blogger_id.value)

    let xhr = new XMLHttpRequest()
    xhr.open('POST', '/blog/save_draft',true);

    // Send Request
    xhr.send(articleData);

    // On Request Complete
    xhr.onload = () => {
        console.log(xhr.responseText)
        const data = JSON.parse(xhr.responseText)
        const message = data["message"].toLowerCase()
        const status = data["status"].toLowerCase()

        // Show response
        flash_response(message,status)
    }

    article_title.value = ""
    article_body.value = ""
})


// Get Attachment Files
const file_upload = document.getElementById("upload")
const audio_files = document.querySelectorAll(".audios")
const image_files = document.querySelectorAll(".images")
const video_files = document.querySelectorAll(".videos")

// Upload Field
const upload_field = document.getElementById("upload_files")
upload_field.addEventListener("click", () => {
    file_upload.click()
})

// Get File Name
file_upload.addEventListener('change', () => {
    let file = file_upload.files[0];
    if(file) {
        uploadFile(file);
        file_upload.value = '';
    }
});

// Append file to article
const is_clicked = document.querySelectorAll(".is_clicked")

is_clicked.forEach((clicked) => {
    clicked.addEventListener("click", (e) => {
        let src_element = clicked.parentElement.children[0]
        const src = src_element.getAttribute("src")

        const article = document.getElementById("content")
        const article_content = article.value

        const updated_value = `${article_content} \n${src}`
        article.value = updated_value
    })
})