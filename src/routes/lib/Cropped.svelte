<script>
    export let allCrops;
    export let filename;

    function save() {
        var downloadClick = document.createElement('a');
        downloadClick.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(JSON.stringify(allCrops, null, "\t")));
        downloadClick.setAttribute('download', filename+'_crops.json');

        downloadClick.style.display = 'none';
        document.body.appendChild(downloadClick);

        downloadClick.click();

        document.body.removeChild(downloadClick);
    }
</script>

<svelte:head>
    <link rel="stylesheet" href="%sveltekit.assets%/cropped.scss" />
</svelte:head>

<div class="section cropped-images-wrapper">
    <div>
        <h6>Images cropped:</h6>
        <div id="cropped-imgs"></div>
    </div>
    <button on:click={save} disabled={allCrops.length == 0} id="save" title="Save"><i class="fa-solid fa-floppy-disk"></i><p>Save</p></button>
</div>
