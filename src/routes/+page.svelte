<script>
    // Code heavily inspired by this: https://stackoverflow.com/questions/27213413/canvas-cropping-images-in-different-shapes

    import { onMount } from 'svelte';

    // media query
    let innerWidth;

    // variables for uploading image
    let input;
    let uploadBtn;

    // canvas-related variables
    let canvas;
    let ctx;
    
    // image to be cropped
    let img;

    // div to store cropped images
    let croppedImgs;

    // an array to hold user's click-points that define the clipping area
    let points = [];
    let rpoints = [];

    // variables for selecting cropping type
    let cropType = 'rectangle';
    let rectangleBtn, polygonBtn;

    // array to hold all the cropped images
    let allCrops = [];

    onMount(() => {
        ctx = canvas.getContext("2d");
        croppedImgs = document.getElementById("cropped-imgs");
    });

    function onFileSelected(e) {
        const reader = new FileReader();
        reader.addEventListener("load", function (evt) {
            var newImg = new Image();
            newImg.onload = function() {
                canvas.classList.remove("hide");
                uploadBtn.classList.add("hide");
                canvas.height = (canvas.width/img.width)*img.height;
                ctx.strokeStyle = "#ED3996";
                ctx.fillStyle = '#ED399650';
                ctx.drawImage(newImg,0,0,newImg.width,newImg.height,0,0,canvas.width,canvas.height);
            }
            if (evt.target && typeof(evt.target.result) == 'string') {
                newImg.src = evt.target.result;
            }
            img = newImg;
        });
        reader.readAsDataURL(e.target.files[0]);
    }

    function setCropType(set) {
        cropType = set;
        if (set == 'rectangle') {
            rectangleBtn.classList.add('selected');
            polygonBtn.classList.remove('selected');
        } else {
            rectangleBtn.classList.remove('selected');
            polygonBtn.classList.add('selected');
        }
        reset();
    }

    function handleMouseDown(e) {
        if (cropType == 'polygon') {
            polygonCrop(e);
        } else if (cropType == 'rectangle') {
            rectangleCrop(e);
        } else {
            console.log('error')
        }
    }

    function polygonCrop(e) {
        // tell the browser that we're handling this event
        e.preventDefault();
        e.stopPropagation();

        // calculate mouseX & mouseY
        let mx = e.pageX-canvas.offsetLeft;
        let my = e.pageY-canvas.offsetTop;

        // push the clicked point to the points[] array
        points = [...points, {x:mx,y:my}]

        // remove points from redo[] array
        rpoints.length = 0
        rpoints = rpoints;

        // show the user an outline of their current clipping path
        outlineIt();

        // if the user clicked back in the original circle
        // then complete the clip
        if (points.length > 1) {
            var dx = mx - points[0].x;
            var dy = my - points[0].y;
            if ( dx*dx+dy*dy < 10*10 ) {
                clipIt();
            }
        }
    }

    function rectangleCrop(e) {
        // tell the browser that we're handling this event
        e.preventDefault();
        e.stopPropagation();

        // calculate mouseX & mouseY
        let mx = e.pageX-canvas.offsetLeft;
        let my = e.pageY-canvas.offsetTop;
        
        // maximum two clicks
        if (points.length < 2) {
            // push the clicked point to the points[] array
            if (points.length == 0) {
                points = [...points, {x:mx,y:my}]
            } else {
                points = [...points, {x:mx,y:points[0].y}, {x:mx,y:my}, {x:points[0].x,y:my}]
            }

            // show the user an outline of their current clipping path
            outlineIt();
        }

        // if the user clicked back in the original circle
        // then complete the clip
        if (points.length > 1) {
            var dx = mx - points[0].x;
            var dy = my - points[0].y;
            if ( dx*dx+dy*dy < 10*10 ) {
                clipIt();
            }
        } 
    }

    // show the current potential clipping path
    function outlineIt() {
        ctx.drawImage(img,0,0,img.width,img.height,0,0,canvas.width,canvas.height);

        if (points.length > 0) {  
            ctx.beginPath();
            ctx.moveTo(points[0].x,points[0].y);
            for(var i=0; i<points.length; i++){
                ctx.lineTo(points[i].x,points[i].y);
            }
            ctx.closePath();
            ctx.fill();
            ctx.stroke();

            // draw beginning circle
            ctx.beginPath();
            ctx.arc(points[0].x,points[0].y,10,0,Math.PI*2);
            ctx.closePath();
            ctx.stroke();
        }
    }

    // removes a point from points[] and adds it to rpoints[]
    function undo() {
        var move = points.pop();
        points = points;
        rpoints = [...rpoints, move];
        outlineIt();
    }

    // removes a point from rpoints[] and adds it to points[]
    function redo() {
        var move = rpoints.pop();
        rpoints = rpoints;
        points = [...points, move];
        outlineIt();
    }

    function reset() {
        rpoints.length = 0;
        rpoints = rpoints;
        points.length = 0;
        points = rpoints;
        outlineIt();
    }

    // clip the selected path to a new canvas
    function clipIt() {
        // calculate the size of the user's clipping area
        var minX = 10000;
        var minY = 10000;
        var maxX = -10000;
        var maxY = -10000;
        for(var i=1;i<points.length;i++){
            var p=points[i];
            if (p.x<minX) { minX=p.x; }
            if (p.y<minY) { minY=p.y; }
            if (p.x>maxX) { maxX=p.x; }
            if (p.y>maxY) { maxY=p.y; }
        }
        var width = maxX-minX;
        var height = maxY-minY;

        // clip the image into the user's clipping area
        ctx.save();
        ctx.clearRect(0,0,canvas.width,canvas.height);
        ctx.beginPath();
        ctx.moveTo(points[0].x,points[0].y);
        for(var i=1; i<points.length; i++){
            var p = points[i];
            ctx.lineTo(points[i].x,points[i].y);
        }
        ctx.closePath();
        ctx.clip();
        ctx.drawImage(img,0,0,img.width,img.height,0,0,canvas.width,canvas.height);
        ctx.restore();

        // create a new canvas 
        var c = document.createElement('canvas');
        var cx = c.getContext('2d');

        // resize the new canvas to the size of the clipping area
        c.width = width;
        c.height = height;

        // draw the clipped image from the main canvas to the new canvas
        if (cx) { cx.drawImage(canvas,minX,minY,width,height,0,0,width,height); }

        // create a new Image() from the new canvas
        var clippedImage = new Image();
        clippedImage.onload = function() {
            // append the new image to the page
            croppedImgs.appendChild(createDiv(clippedImage));
        }
        clippedImage.src = c.toDataURL();

        // add to allCrops{}
        allCrops = [...allCrops, { id:allCrops.length, points:points.slice() }];

        // clear the previous points 
        points.length = 0;

        // redraw the image on the main canvas for further clipping
        ctx.drawImage(img,0,0,img.width,img.height,0,0,canvas.width,canvas.height);
    }

    function createDiv(clippedImage) {
        clippedImage.id = "crop-"+croppedImgs.children.length;

        let deleteBtn = document.createElement("button");
        deleteBtn.id = "deleteBtn-"+croppedImgs.children.length;
        deleteBtn.classList.add('icon-button');
        deleteBtn.innerHTML = '<i class="fa-solid fa-circle-minus" id="minusIcon-'+croppedImgs.children.length+'"></i>';
        deleteBtn.addEventListener("click", deleteCrop);

        let div = document.createElement('div');
        div.classList.add('cropped-img-div');
        div.id = "cropDiv-"+croppedImgs.children.length;
        div.appendChild(clippedImage);
        div.appendChild(deleteBtn);

        return div;
    }

    function deleteCrop(e) {
        let idText = e.target.id.split('-');
        let idNum = idText[idText.length-1];

        allCrops.splice(allCrops.indexOf(allCrops.find(x=>x.id == idNum)), 1);
        let id = document.getElementById('cropDiv-'+idNum);
        if (id) { id.remove(); }
    }

    function handleMouseMove(e) {
        // tell the browser that we're handling this event
        e.preventDefault();
        e.stopPropagation();

        // calculate mouseX & mouseY
        let mx = e.pageX-canvas.offsetLeft;
        let my = e.pageY-canvas.offsetTop;

        if (img) { 
            ctx.clearRect(0,0,canvas.width,canvas.height);
            ctx.drawImage(img,0,0,img.width,img.height,0,0,canvas.width,canvas.height);
            outlineIt();

            // draw lines
            ctx.beginPath();
                // draw x-axis
                ctx.moveTo(mx,0);
                ctx.lineTo(mx, my-10);
                ctx.moveTo(mx,my+10);
                ctx.lineTo(mx, canvas.height);
                // draw y-axis
                ctx.moveTo(0,my);
                ctx.lineTo(mx-10, my);
                ctx.moveTo(mx+10,my);
                ctx.lineTo(canvas.width, my);
            ctx.closePath();
            ctx.stroke(); 
        }      
    }

    function save() {
        console.log(JSON.stringify(allCrops));
    }

    function deleteImage() {
        canvas.classList.add("hide");
        uploadBtn.classList.remove("hide");
        input.value = null;
        allCrops = [];
        reset();
        img = undefined;
        while (croppedImgs.firstChild) {
            croppedImgs.removeChild(croppedImgs.firstChild);
        }
    }
</script>

<svelte:window bind:innerWidth={innerWidth}/>

<div class="section header">
    <h2>Pikrex Cropping Tool</h2>
</div>
<div class="main-body" class:hide="{innerWidth < 767}">
    <div class="section left">
        <div class="canvas">
            <canvas 
                bind:this={canvas}
                width="500"
                height="750"
                on:mousedown={(e)=>handleMouseDown(e)} 
                on:mousemove={(e)=>handleMouseMove(e)} 
                class="hide"
                >
            </canvas>
            <button class="upload-button" bind:this={uploadBtn} on:click={input.click()}>
                <i class="fa-solid fa-images"></i>
                <h6>Upload image</h6>
            </button>
            <input type="file" accept=".jpg, .jpeg, .png" class="hide" bind:this={input} on:change={(e)=>onFileSelected(e)}>
        </div>
        <div class="buttons">
            <button bind:this={rectangleBtn} on:click={()=>setCropType('rectangle')} disabled={img == undefined} class="icon-button selected" title="Rectangle Crop"><i class="fa-solid fa-crop-simple"></i></button>
            <button bind:this={polygonBtn} on:click={()=>setCropType('polygon')} disabled={img == undefined} class="icon-button" title="Polygon Crop"><i class="fa-solid fa-draw-polygon"></i></button>
            <button on:click={reset} disabled={points.length == 0} class="icon-button" title="Reset"><i class="fa-solid fa-broom"></i></button>
            <button on:click={undo} disabled={points.length == 0} class="icon-button" title="Undo"><i class="fa-solid fa-rotate-left"></i></button>
            <button on:click={redo} disabled={rpoints.length == 0} class="icon-button" title="Redo"><i class="fa-solid fa-rotate-right"></i></button>
            <button on:click={deleteImage} disabled={img == undefined} class="icon-button" title="Delete"><i class="fa-solid fa-trash"></i></button>
        </div>
    </div>
    <div class="section right">
        <div>
            <h6>Images cropped:</h6>
            <div id="cropped-imgs"></div>
        </div>
        <button on:click={save} disabled={allCrops.length == 0} id="save" title="Save"><i class="fa-solid fa-floppy-disk"></i><p>Save</p></button>
    </div>
</div>
<div class="section main-body" class:hide="{innerWidth > 767}">
    <p>Seems like the screen is too small!</p>
</div>
<div class="section footer">
    <p>Copyright Pikrex Inc. 2023</p>
</div>

<style lang="scss">
    @import url('https://fonts.googleapis.com/css2?family=Akshar:wght@300;700&display=swap');

    $black: #121212;
    $dark_grey: #404040;
    $white: #FFFFFF;
    $pink: #ED3996;
    $light_pink: #FAC7E1;
    $dark_pink: #D51477;

    // Section styling
    .section {
        padding: 32px;
    }

    // Header and Footer
    .header, .footer {
        display: grid;
        place-items: center;
    }

    // Main Body
    .main-body {
        background: $white;
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 24px;

        .left {
            flex: 1 0 500px;

            display: flex;
            gap: 8px;

            .canvas {
                canvas {
                    border: 1px solid #d3d3d3;
                    cursor: crosshair;
                }
            
                .upload-button {
                    width: 500px;
                    height: 750px;
                    background: transparent;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    gap: 8px;
                    border: 1px solid #d3d3d3;

                    i {
                        font-size: 64px;
                    }
                }
            }
            
            justify-content: center;
            @media screen and (min-width: 1025px) {
                justify-content: end;
            }
            
            .buttons {
                display: flex;
                flex-direction: column;
                gap: 8px;

                .selected {
                    color: $pink;
                }
            }
        }

        .right {
            flex: 1 0 400px;

            display: flex;
            flex-direction: column;
            justify-content: space-between;

            #save {
                display: flex;
                gap: 8px;
                justify-content: center;
                align-items: center;
                border-radius: 1000px;
                padding: 8px 32px;
                border: 2px solid $pink;
                width: max-content;    

                &:hover {
                    border: 2px solid $dark-pink;
                }

                i {
                    font-size: 16px;
                    color: $black;
                }
            }

            #cropped-imgs {
                display: flex;
                flex-direction: column;
                gap: 8px;
            }
        }
    }

    button:disabled {
        opacity: 0.5;
    }

    .hide {
        display: none !important;
    }

    :global(.icon-button) {
        background: transparent;
        border: none;

        &:hover {
            color: $dark_pink;
        }
        
        &:disabled {
            color: $dark_grey;
        }
    }
    :global(.icon-button > i) {
        font-size: 32px;
    }
    :global(.cropped-img-div) {
        border: solid 2px $light_pink;
        padding: 16px;
        border-radius: 8px;
        display: flex;
        justify-content: space-between;
    }
</style>
