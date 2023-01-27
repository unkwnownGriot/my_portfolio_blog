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

    const approved_category = ["audio","video","image"]

    // File Info
    const fileName = file.name;
    let fileSize = file.size;
    let fileType = file.type;
    let folder = fileType.split('/')[0]

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
        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/blog/file_upload',true);

        // Update Progress Bar
        let uploader = xhr.upload

        // Uploader Upload
        uploader.addEventListener('progress', (e) => {
            let progressHTML =   `<p>Uploading...</p>`;
            upload_field.innerHTML = progressHTML;
        });

        // Send Request
        xhr.send(fileData);

        // On Request Complete
        xhr.onload = () => {
            const data = JSON.parse(xhr.responseText)
            const message = data["message"].toLowerCase()
            const status = data["status"].toLowerCase()

            // Remove Progress Bar
            upload_field.innerHTML = `<p>Upload Files</p>`;

            const article = document.getElementById("content")
            const article_content = article.value

            if (file_category == "image" | file_category == "images"){
                const updated_value = `${article_content} \n![](/blog/static/${folder}/${new_file_name})`
                article.value = updated_value
            }

            else if (file_category == "video"){
                const updated_value = `${article_content} \n[](/blog/static/${folder}/${new_file_name})`
                article.value = updated_value
            }

            // Show response
            flash_response(message,status)
        }
        
    }
    else{
        flash_response("Attempt to upload invalid file","warning")
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
        const hiddenElements = article.children[1]
        const postTypeElement = hiddenElements.children[0]
        const post_type = postTypeElement.value

        if (post_type.toLowerCase() == "plain post"){
            const typeElement = document.querySelector(".plain_post")
            typeElement.click()
        }
        else if (post_type.toLowerCase() == "image post"){
                const typeElement = document.querySelector(".image_post")
                typeElement.click()
        }
        else if (post_type.toLowerCase() == "images post"){
                const typeElement = document.querySelector(".images_post")
                typeElement.click()
        }
        else if (post_type.toLowerCase() == "video post"){
                const typeElement = document.querySelector(".video_post")
                typeElement.click()
            }
        else if (post_type.toLowerCase() == "audio post"){
                const typeElement = document.querySelector(".audio_post")
                typeElement.click()
            }

        // set category
        const articleCartegoryElement = hiddenElements.children[2]
        const articleCartegory = articleCartegoryElement.value
        const select_field = document.getElementById("select_field")
        select_field.value = articleCartegory

        // Set Title
        const article_title = article.children[2].children[0].innerText
        const article_name = document.querySelector(".content_header")
        article_name.value = article_title

        // Display in article create section
        const article_content = hiddenElements.children[3].value
        const article_textarea = document.querySelector(".content")
        article_textarea.value = article_content

        // add update button display
        remove_display(draft_article)
        fix_display(update_article)
    })
})


// article actions
const delete_buttons = document.querySelectorAll(".delete")
delete_buttons.forEach((delete_button) => {
    delete_button.addEventListener("click",() => {
        
        const article = delete_button.parentElement.parentElement.parentElement
        const article_id = article.children[1].children[1].value
    
        const articleForm = new FormData();
        articleForm.append('csrf_token', csrf_token.value)
        articleForm.append("article_id", article_id)

        let xhr = new XMLHttpRequest()
        xhr.open('POST', '/blog/delete_article',true);

        // Send Request
        xhr.send(articleForm);

        // On Request Complete
        xhr.onload = () => {
            const data = JSON.parse(xhr.responseText)
            const message = data["message"].toLowerCase()
            const status = data["status"].toLowerCase()

            // Show response
            flash_response(message,status)

            if (status == "success"){
                article.classList.add("remove_display")
            }
        }
    })
})


// buttons
const new_article = document.getElementById("new")
const draft_article = document.getElementById("draft")
const publish_article = document.getElementById("publish")
const update_article = document.getElementById("update")
const preview_article = document.getElementById("preview")


// Create New Article interface
new_article.addEventListener('click', (e) => {
    e.preventDefault()

    const article_title = document.getElementById("content_header")
    const article_body = document.getElementById("content")

    remove_display(update_article)
    fix_display(draft_article)

    article_title.value = ""
    article_body.value = ""

    articles.forEach((article) => {
        article.classList.remove("viewing")
    })
})


// Save to draft
draft_article.addEventListener('click',(e) => {
    e.preventDefault()

    const article_title = document.getElementById("content_header")
    const article_body = document.getElementById("content")
    const post_type = document.querySelectorAll(".select")
    const blogger_id = document.getElementById("blogger_id")
    const post_text = post_type[0].innerText.toLowerCase()
    let category = null

    // artcle category
    if (article_checkbox_marker.classList.contains('remove_display')){
        category = document.getElementById("select_field").value
    }
    else{
        category = document.getElementById("category_name").value
    }

    if (category == ""){
        flash_response("Article category not set","warning")
        return
    }

    if (article_title.value == ""){
        flash_response("Article title can't be empty","warning")
        return
    }

    if (article_body.value == ""){
        flash_response("Article content can't be empty","warning")
        return
    }

    const articleData = new FormData();
    articleData.append('csrf_token', csrf_token.value)
    articleData.append('title', article_title.value);
    articleData.append('body',article_body.value)
    articleData.append("post_type",post_text)
    articleData.append("category",category)
    articleData.append("author_uid", blogger_id.value)

    let xhr = new XMLHttpRequest()
    xhr.open('POST', '/blog/save_draft',true);

    // Send Request
    xhr.send(articleData);

    // On Request Complete
    xhr.onload = () => {
        const data = JSON.parse(xhr.responseText)
        const message = data["message"].toLowerCase()
        const status = data["status"].toLowerCase()

        // Show response
        flash_response(message,status)
    }

    article_title.value = ""
    article_body.value = ""
    attachment = []
})


// Publish article
publish_article.addEventListener('click',(e) => {
    e.preventDefault()

    const article_title = document.getElementById("content_header")
    const article_body = document.getElementById("content")
    const post_type = document.querySelectorAll(".select")
    const blogger_id = document.getElementById("blogger_id")
    const post_text = post_type[0].innerText.toLowerCase()
    let category = null

    // artcle category
    if (article_checkbox_marker.classList.contains('remove_display')){
        category = document.getElementById("select_field").value
    }
    else{
        category = document.getElementById("category_name").value
    }

    if (category == ""){
        flash_response("Article category not set","warning")
        return
    }

    if (article_title.value == ""){
        flash_response("Article title can't be empty","warning")
        return
    }

    if (article_body.value == ""){
        flash_response("Article content can't be empty","warning")
        return
    }

    const articleData = new FormData();
    articleData.append('csrf_token', csrf_token.value)
    articleData.append('title', article_title.value);
    articleData.append('body',article_body.value)
    articleData.append("post_type",post_text)
    articleData.append("category",category)
    articleData.append("author_uid", blogger_id.value)

    let xhr = new XMLHttpRequest()
    xhr.open('POST', '/blog/publish_article',true);

    // Send Request
    xhr.send(articleData);

    // On Request Complete
    xhr.onload = () => {
        const data = JSON.parse(xhr.responseText)
        const message = data["message"].toLowerCase()
        const status = data["status"].toLowerCase()

        // Show response
        flash_response(message,status)
    }

    article_title.value = ""
    article_body.value = ""
    attachment = []
})


// Update article
update_article.addEventListener("click", (e) => {
    e.preventDefault()

    const article = document.querySelector(".viewing")
    const article_id = article.children[1].children[1].value
    const article_title = document.getElementById("content_header").value
    const article_content = document.getElementById("content").value
    const old_content = article.children[1].children[3]
    old_content.value = article_content

    const articleUpdate = new FormData()
    articleUpdate.append('csrf_token', csrf_token.value)    
    articleUpdate.append("article_id", article_id)
    articleUpdate.append("header", article_title)
    articleUpdate.append("content", article_content)

    let xhr = new XMLHttpRequest()
    xhr.open('POST', '/blog/update_article',true);

    // Send Request
    xhr.send(articleUpdate);

    // On Request Complete
    xhr.onload = () => {
        console.log(xhr.responseText)
        const data = JSON.parse(xhr.responseText)
        const message = data["message"].toLowerCase()
        const status = data["status"].toLowerCase()

        // Show response
        flash_response(message,status)
    }  
})


// Preview article
// preview_article.addEventListener("click", (e) => {

//     const header = document.getElementById("content_header").value
//     const content = document.getElementById("content").value

//     const articleData = new FormData();
//     articleData.append('csrf_token', csrf_token.value)
//     articleData.append('header', header);
//     articleData.append('content', content)

//     let xhr = new XMLHttpRequest()
//     xhr.open('POST', '/blog/save_draft',true);

//     // Send Request
//     xhr.send(articleData);

//     // On Request Complete
//     xhr.onload = () => {
//         const data = JSON.parse(xhr.responseText)
//         const message = data["message"].toLowerCase()
//         const status = data["status"].toLowerCase()

//         // Show response
//         flash_response(message,status)
//     }

// })



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
        const approved_images = ["png","jpg","jpeg","gif"]
        const approved_videos = ["mp4","avi","mov","wmv"]
        const approved_audios = ["mp3","m4a","wav"]

        file_extension = src.split('.')[1]
        console.log(file_extension)

        if (approved_images.includes(file_extension)){
            const updated_value = `${article_content} \n![](${src})`
            article.value = updated_value
        }

        else if (approved_videos.includes(file_extension)){
            let raw = `<video controls src="${src}" type="video/${file_extension}"></video>`

            const updated_value = `${article_content} \n${raw}`
            article.value = updated_value
        }

        else if (approved_audios.includes(file_extension)){
            let raw = `<audio controls src="${src}"></audio>`

            const updated_value = `${article_content} \n${raw}`
            article.value = updated_value
        }
    })
})