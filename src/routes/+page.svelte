<script>
    import {Cropper, Cropped} from 'polygon-crop-tool';

    // variables to download all the cropped images
    let allCrops = [];
    let filename;

    // colours
    let colours = {
        primary: '#ED3996', // cropping lines + fill
        secondary: '#3B97ED', // axis lines
        tooltip: '#121212',
        tooltip_text: '#FFFFFF',
    }

    // media query
    let innerWidth;

</script>

<svelte:window bind:innerWidth={innerWidth}/>

<div class="section header">
    <img src="/favicon.png" alt="logo"/>
</div>
<!-- App can only be used on tablet size and up. -->
<div class="section main-body" class:hide="{innerWidth < 767}">
    <Cropper cwidth=500 cheight=750 colours={colours} bind:allCrops={allCrops} bind:filename={filename}/>
    <Cropped colours={colours} bind:allCrops={allCrops} bind:filename={filename}/>
</div>
<div class="section main-body" class:hide="{innerWidth > 767}">
    <p>Seems like the screen is too small!</p>
</div>

<div class="section footer">
    <p>Copyright 2023. Pikrex Inc.</p>
</div>

<style lang="scss">
    $black: #121212;
    $dark_grey: #404040;
    $white: #FFFFFF;
    $pink: #ED3996;
    $light_pink: #FAC7E1;
    $dark_pink: #D51477;
    $blue: #3B97ED;

    .header,
    .footer {
        display: grid;
        gap: 8px;
        place-items: center;
    }

    .header img {
        height: 48px;
    }

    .footer p {
        color: $white;
    }

    .main-body {
        background: $white;
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 24px;
    }

    .hide {
        display: none !important;
    }

    // styling the components
    @media screen and (min-width: 1025px) {
        :global(.cropper-wrapper) {
            justify-content: end !important;
        }
    }

    :global(.upload-button) {
        background: transparent;

        :global(span) {
            color: $black;
        }
    } 

    :global(.cropped-img-div) {
        border: solid 2px $blue !important;
    }

    :global(.save-buttons > button) {
        border-radius: 1000px;
        padding: 8px 32px;
        border: 2px solid $pink;
        background: transparent;
    }
</style>