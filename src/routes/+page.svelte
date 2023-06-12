<script>
	import Cropper from './components/Cropper.svelte';
	import Cropped from './components/Cropped.svelte';

    // variables to download all the cropped images
    let allCrops = [];
    let filename;

    // media query
    let innerWidth;

</script>

<svelte:window bind:innerWidth={innerWidth}/>

<div class="section header">
    <h2>Pikrex Cropping Tool</h2>
</div>
<!-- App can only be used on tablet size and up. -->
<div class="main-body" class:hide="{innerWidth < 767}">
    <Cropper bind:allCrops={allCrops} bind:filename={filename}/>
    <Cropped bind:allCrops={allCrops} bind:filename={filename}/>
</div>
<div class="section main-body" class:hide="{innerWidth > 767}">
    <p>Seems like the screen is too small!</p>
</div>
<div class="section footer">
    <p>Copyright Pikrex Inc. 2023</p>
</div>

<style lang="scss">

    // Header and Footer
    .header, .footer {
        display: grid;
        place-items: center;
    }

    // Main Body
    .main-body {
        background: #FFFFFF;
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 24px;
    }

    .hide {
        display: none !important;
    }
</style>
