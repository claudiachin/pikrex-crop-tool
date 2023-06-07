<script>
    import { onMount } from 'svelte';

    // <input> to upload image
    let input;

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

    // select cropping type
    let cropType = 'polygon';

    onMount(() => {
        ctx = canvas.getContext("2d");
        croppedImgs = document.getElementById("cropped-imgs");
    });

    function onFileSelected() {
        const reader = new FileReader();
        reader.addEventListener("load", function (evt) {
            var newImg = new Image();
            newImg.onload = function() {
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
        reader.readAsDataURL(input.files[0]);
    }

    function toggleCrop() {
        cropType = cropType == 'rectangle' ? 'polygon' : 'rectangle';
        console.log(cropType);
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
            var p=points[i];
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
        c.width=width;
        c.height=height;

        // draw the clipped image from the main canvas to the new canvas
        if (cx) { cx.drawImage(canvas,minX,minY,width,height,0,0,width,height); }

        // create a new Image() from the new canvas
        var clippedImage=new Image();
        clippedImage.onload=function() {
            // append the new image to the page
            croppedImgs.appendChild(clippedImage);
        }
        clippedImage.src=c.toDataURL();

        // clear the previous points 
        points.length=0;

        // redraw the image on the main canvas for further clipping
        ctx.drawImage(img,0,0,img.width,img.height,0,0,canvas.width,canvas.height);
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
</script>

<div class="section header">
    <h2>Pikrex Cropping Tool</h2>
</div>
<div class="main-body">
    <div class="section crop-image">
        <canvas 
            bind:this={canvas}
            width="500"
            height="750"
            on:mousedown={(e)=>handleMouseDown(e)} 
            on:mousemove={(e)=>handleMouseMove(e)} 
            style="border:1px solid #d3d3d3;"
            >
        </canvas>
    </div>
    <div class="section cropped">
        <input type="file" accept=".jpg, .jpeg, .png" bind:this={input} on:change={onFileSelected}><br>
        <div class="buttons">
            <button on:click={toggleCrop}>Rectangle</button>
            <button on:click={toggleCrop}>Polygon</button>
            <button on:click={reset} disabled={points.length == 0}>Reset</button>
            <button on:click={undo} disabled={points.length == 0}><i class="fa-solid fa-rotate-left"></i></button>
            <button on:click={redo} disabled={rpoints.length == 0}><i class="fa-solid fa-rotate-right"></i></button>
        </div>
        <div class="cropped-imgs">
            <p>Images cropped:</p>
            <div id="cropped-imgs"></div>
        </div>
        <div class="instructions">
            <p>Intructions:</p>
            <p>1. Upload your image.</p>
            <p>2. </p>
        </div>
    </div>
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
    $transparent: rgba(0,0,0,0);

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

        .crop-image {
            flex: 1 0 500px;

            input, canvas {
                float: right;
            }

            @media screen and (max-width: 1024px) {
                display: flex;
                justify-content: center;

                input, canvas {
                    float: none;
                }
            }
        }

        .cropped {
            flex: 1 0 400px;
        }

        canvas {
            cursor: crosshair;
        }
    }

    button:disabled {
        opacity: 0.5;
    }
</style>
