<template>

    <div class="wrapper">

        <!-- search section has bg image -->
        <div class="search-section">
        
            <!-- Search Input + Autocomplete -->
            <div class="search-container">

                <div class="search-bar-wrapper">
                    <input 
                    v-model="query" 
                    placeholder="start typing, e.g. species: ind..." @input="handleInput" 
                    @focus="handleFocus"
                    @click="handleInput"
                    @keydown.down="handleArrowKey('down')"
                    @keydown.up="handleArrowKey('up')"
                    @keydown.enter="handleEnter"
                    @keydown.esc="clearSuggestions"
                    class="search-bar" 
                    :class="{ 'no-bottom-radius': suggestions.length }" ref="searchInput" />
                    
                    <button class="search-icon" @click="handle">
                        <i class="fa fa-search"></i>
                    </button>
                </div>
            

                <!-- Autocomplete Suggestions  -->
                <div v-if="suggestions.length" class="autocomplete-dropdown">
                    <div v-if="areKeywords(suggestions)" class="keyword-label">Keywords</div>
                    <ul>
                        <li v-for="(suggestion, index) in suggestions" :key="index" 
                        @click="applyFilter(suggestion)"
                        :class="{ 'highlighted': selectedIndex === index }">
                            {{ suggestion }}
                        </li>
                    </ul>
                </div>

            </div>
        </div>

        <!-- NFT Section
            This section is made up of 4 parts: 
            1. A carousel with smaller, user submitted  pics
            2. The NFT generated based on the user pic
            3. A description of the image submitted by the user 
            4. A add picture button at the bottom
        -->
        <div v-if="isNftMode">

            <!-- NFT Carousel -->
            <div class="nft-carousel">
                <div class="nft-carousel-container">
                    <img v-for="(image, index) in visibleImages" 
                        :src="image" 
                        :key="index" 
                        class="nft-image" 
                        @click="setCurrentImage(index)"/>
                </div>
            </div>

            <!-- Info Box for Selected Image -->
             <div class="nft-info-box">
                <div class="nft-info-left">
                    <img :src="getPicImage()" alt="Real Picture" class="nft-info-image">
                </div>
                <div class="nft-info-right">
                    <p class="nft-info-text">{{ fetchedText  }}</p>
                </div>
             </div>

             <!-- Add image button -->
              <button class="nft-plus-button">+</button>
        </div>

        <!-- Results section
             - Split container layout for search results and sanctuary info 
             - TODO(prashanth@): rename joined-box
        -->
        <div class="joined-box" v-if="filteredSanctuaries.length">

            <!-- Search results  -->
            <div class="results-box">
                <div
                class="sanctuary-row"
                v-for="sanctuary in filteredSanctuaries"
                :key="sanctuary.sanctuary"
                @click="selectSanctuary(sanctuary)">
                    <!-- First row: sanctuary name -->
                    <div class="sanctuary-name">
                        {{ sanctuary.sanctuary }}
            
                        <!-- Display matching badges along name -->
                         
                         <div v-if="displayBadgesInResults">
                             <img
                             v-for="image in getMatchingBadges(sanctuary.species)"
                             :key="image"
                             :src="image"
                             :alt="`Badge for ${image}`"
                             class="badge">
                         </div>
                    </div>
                </div>
            </div>

            <div class="vertical-line"></div>

            <!-- Sanctuary info box (two-column layout) -->
            <Transition name="fade-slide">
                <div class="sanctuary-info-box" v-if="selectedSanctuary">
                
                    <div class="title-bar">
                        <div class="sanctuary-title">
                            {{ selectedSanctuary.sanctuary }}
                        </div>
                        <div class="tab-bar">
                            <button 
                            class="tab" 
                            :class="{ active: activeTab === 'map'}" 
                            @click="setActiveTab('map')">
                                Maps
                            </button>
                            <button 
                            class="tab" 
                            :class="{ active: activeTab === 'research' }" 
                            @click="setActiveTab('research')">
                                Research
                            </button>
                        </div>
                    </div>

                    <hr class="horizontal-line">
                    <div class="info-container">
                        <!-- Left column: sanctuary info -->
                        <div class="info-left">
                            <div class="stylised-text">
                                {{ selectedSanctuary.sanctuary }} is a wildlife reserve in {{ selectedSanctuary.state }}
                                ({{ selectedSanctuary.district }}) with {{ selectedSanctuary.species.length }} species
                                and {{ Object.keys(selectedSanctuary.ngo).length }} NGOs. It spans an area of {{ selectedSanctuary.area }}
                                with a population of {{ selectedSanctuary.population }} and
                                {{ selectedSanctuary.safari ? 'offers' : 'does not offer' }} safaris to the public.
                
                
                                <p><strong>Species: </strong>{{ selectedSanctuary.species.join(', ') }}</p>
                                <p><strong>NGOs: </strong>{{ Object.keys(selectedSanctuary.ngo).join(', ') }}</p>
                                <p><strong>Sightings (last 6w): </strong></p>
                                <div class="badges">

                                    <!-- TODO(prashanth@): this is a hack to display the user submitted badge as an image -->
                                    <img 
                                    v-if="userImage"
                                    :src="userImage" 
                                    alt="User Badge" 
                                    class="badge user-badge"
                                    :class="{ blurred: isLoading }"
                                    @click="handleBadgeClick(userImage)"
                                    >

                                    <!-- Display remaining badges -->
                                    <img
                                    v-for="image in nftImages"
                                    :key="image"
                                    :src="image"
                                    :alt="`Badge for ${image}`"
                                    class="badge"
                                    @click="handleBadgeClick(image)"
                                    :style="{ animationDelay: getBadgeDelay(index) }"
                                    >
                                    <!-- + = "Add a sighting" button
                                         This has to be in a div becaue the animation uses ::before, which doesn't work on img.
                                     -->
                                    <div class="plus-badge-container">
                                        <img src="/images/icons/plus.png" alt="Add sighting" class="plus-badge badge" @click="handleAddButton()">
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="vertical-divider"></div>
                        <!-- Right column: badges -->
                        <div class="info-right">
                            <!-- TODO(prashanth@): rename map-container -->
                            <div class="map-container">
                                <!-- Map image generated at simplemaps.com -->
                                <img src="/images/maps/country.svg" alt="Country Map" class="map-image" v-if="activeTab === 'map'">

                                <div v-if="activeTab === 'research'" class="vhs-stack">
                                    <div
                                    v-for="(paper, index) in researchPapers.slice(0, 5)" 
                                    :key="index"
                                    class="vhs-tape"
                                    @click="handleResearchClick(paper)"
                                    >
                                        <div class="vhs-label">
                                            <div class="vhs-title-sticker">
                                                {{ paper.title }} 
                                            </div>
                                        </div>
                                    </div>
                                    <div v-if="selectedPaper" class="abstract-section stylised-text">
                                        <div class="tv-screen">
                                            <p>{{ typedTitle }}</p>
                                            <p>{{ typedAbstract }}</p>

                                            <!-- Actions a user can take on the paper. -->
                                            <div class="paper-actions">
                                                <a
                                                v-if="showFullPaperLink"
                                                :href="selectedPaper.link" target="_blank" rel="noopener">
                                                    Read Full Paper
                                                </a>
                                                <button 
                                                v-if="showFullPaperLink"
                                                class="play-button" @click="togglePlay">
                                                   <img src="/images/icons/play.png" alt="Play" class="play-icon" />
                                                </button>
                                            </div>
                                        </div>
                                        <!-- Audio element to play the mp3 file -->
                                        <audio ref="audioPlayer" :src="audioSource"></audio>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </Transition>
        </div>

        <!-- Popup modal -->
        <!-- Popup for plus button -->
        <Transition class="fade">
            <div v-if="showAddSightingPopup" class="popup-overlay stylised-text">
                    
                <div class="add-sighting-popup">

                    <!-- Close button similar to the badge popup -->
                    <button class="popup-close" @click="closeAddSightingPopup">&times;</button>

                    <!-- Caption input for the plus button popup -->
                    <input 
                    type="text" 
                    placeholder="What did you see in the wild?"
                    class="popup-text-input"
                    />

                    <!-- Display uploaded image OR the file upload -->
                    <div v-if="uploadedImage">
                        <img :src="uploadedImage" alt="Uploaded Image" class="uploaded-image">
                    </div>
                    <div v-else 
                    class="file-upload-box"
                    @click="triggerFileUpload"
                    >
                        <span class="upload-text">
                            + choose your picture, make sure it has the right time and location
                        </span>
                        <input 
                        type="file" 
                        ref="fileInput"
                        @change="previewImage"
                        class="file-input"
                        />
                    </div>

                    <!-- Confirmation button for the file upload event -->
                    <button class="confirm-button" @click="handleConfirm" v-if="uploadedImage">
                        OK?
                    </button>
                </div>
            </div>
        </Transition>

        <!-- Popup for badge click -->
        <div v-if="showPopup" @click.self="closePopup" class="popup-overlay">
            <div class="popup-card">
                <!-- Popup image with blurred background -->

                <div class="popup-image-container">
                    <img :src="currentImage" alt="Popup Image" class="popup-image">
                    <!-- Popup image scroller to switch between nft <-> real
                         This works as follows:
                         - Initially, currentImageIndex = 0
                         - currentImage returns the selectedBadgeImage
                         - User clicks on the second span below
                         - switchImage sets the currentImageIndex to 1
                         - The computed property for currentImage is re-computed
                         - A new rendering is triggered that updates the above img
                         - The same render pass applies the "active" class
                     -->
                    <div class="image-nav">
                        <span
                        :class="{ active: currentImageIndex === 0 }"
                        @click="switchImage(0)"
                        class="nav-dot"></span>
                        <span
                        :class="{ active: currentImageIndex === 1 }"
                        @click="switchImage(1)"
                        class="nav-dot"></span>
                    </div>
                </div>

                <!-- Popup description -->
                <div class="popup-description">

                    <!-- Banner of popup description -->
                    <div class="popup-description-topbar">

                        <!-- Username and time -->
                        <div class="popup-description-username">
                            <span>beeps</span>
                            <span style="margin-left: 1em;">6w</span>
                        </div>

                        <!-- Popup close button: x -->
                        <button class="popup-close" @click="closePopup">&times;</button>
                    </div>

                    <div class="popup-description-content">
                        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec vel.</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Experiments and tests -->

        <!-- <div class="badge-box">
            <img
            v-for="image in nftImages"
            :key="image"
            :src="image"
            alt="Badge for ${image}" class="badge"
            />
        </div> -->
    </div>
</template>

<script>
export default {
    data() {
        return {
            query: '',
            data: null, 
            suggestions: [],
            // selectedIndex tracks the currently highlighted suggestion for 
            // autocomplete
            selectedIndex: -1,
            filters: [],
            filteredSanctuaries: [],
            keywordOptions: ['species: ', 'sanctuary: ', 'state: ', 'ngo: '],
            // Toggle to show NFT mode
            // TODO: Make this false
            isNftMode: false, 
            // generated manually with: 
            // $ cd public/images/nft nft && ls *.{png,jpg,jpeg,gif,svg} \
            //     2>/dev/null | awk '{print "\x27/images/nft/" $0 "\x27,"}'
            nftImages: [
                '/images/nft/bear.png',
                '/images/nft/cobra.png',
                '/images/nft/crocodile.png',
                '/images/nft/deer.png',
                '/images/nft/dolphin.png',
                '/images/nft/eagle.png',
                '/images/nft/elephant.png',
                '/images/nft/gator.png',
                '/images/nft/gaur.png',
                '/images/nft/honeybadger.png',
                '/images/nft/hornbill.png',
                '/images/nft/jackal.png',
                '/images/nft/leopard.png',
                '/images/nft/lion.png',
                '/images/nft/panther.png',
                '/images/nft/python.png',
                '/images/nft/redpanda.png',
                '/images/nft/snake.png',
                '/images/nft/snowleopard.png',
                '/images/nft/tiger.png',
                '/images/nft/turtlle.png',
                '/images/nft/vulture.png',
                '/images/nft/wolf.png',
            ], 
            visibleImages: [],
            fetchedText: "",
            // If true, badges are displayed alongside search results. 
            displayBadgesInResults: false,
            // If true, several UI options that would other wise need user 
            // input are displayed by default, eg: sanctuaries list. 
            debugMode: false,
            selectedSanctuary: null,

            // Popup handling
            selectedBadge: '/images/nft/honeybadger.png',

            // Initialize to true to show popup on load.
            showPopup: false,
            // A counter used to carousel through images. 
            // In (the now defunct) "nft mode" this is used to cycle 
            // through images. In "popup image" mode, this is used to 
            // cycle through the nft image and the real picture. 
            currentImageIndex: 0,
            showAddSightingPopup: false,
            // Tab navigation starts off showing the map
            activeTab: 'map',
            // Placeholder till actual image upload is handled. 
            // This pointer holds the image location to use in the user 
            // submitted badge.
            userImage: null,
            // Loading state for the new badge (blurred)
            isLoading: true, 
            // A preview of the user uploaded image
            uploadedImage: null,
            // To store research papers from JSON scraped from google scholar.
            researchPapers: [],
            // Which vhs-tape/paper was selected.
            selectedPaper: null,

            // Typing settings, for the abstract getting typed out. 
            typedTitle: "", 
            typedAbstract: "",
            typingSpeed: 5, 
            // A flag used to hide the paper link till the typing is done. 
            showFullPaperLink: false,
            // Audio section
            audioSource: '/audio/slothbear1.mp3',
            isPlaying: false,
        };
    },
    computed: {
        currentImage() {
            return this.currentImageIndex === 0 ? this.selectedBadge : this.getPicForSelectedBadge();
        }
    },
    mounted() {
        fetch('/data/sanctuaries_data.json')
            .then(response => response.json())
            .then(data => {
                this.data = data;
                if (this.debugMode) {
                    this.filteredSanctuaries = data.sanctuaries_data;
                    this.selectedSanctuary = this.filteredSanctuaries[0];
                }
            }
        );
        fetch('/data/research_data.json')
            .then(response => response.json())
            .then(data => {
                this.researchPapers = data;
            })
            .catch(error => {
                console.error("Error loading research papers: ", error)
            });

        // NFT mode handlers
        this.updateVisibleImages();
    },
    methods: {
        /* handling scrolling 
         * 
         * We use a counter to track the number of up/down key presses. When 
         * the enter keystroke is received, this counter is used as an index 
         * into the suggestions array, and the  chosen suggestion is passed 
         * into applyFilter, which processes it just like it would process a 
         * mouse click.  
         * 
         * The highlight is applied via a conditional class on the li element. 
         * The condition for application of this class depends on 
         * selectedIndex. 
         */
        handleArrowKey(direction) {
            if (
                direction === 'down' && 
                this.selectedIndex < this.suggestions.length - 1) {
                    this.selectedIndex ++;
                } else if (direction === 'up' && this.selectedIndex > 0) {
                    this.selectedIndex --;
                }
                // TODO(prashanth@): else this.selectedIndex === this.suggestions.length 
        },
        /* Handling enter
         * 
         * If the user is scrolling assume they're going through the 
         * autocomplet dropdown. In this case, we need to copy the 
         * autocomplete suggestion into the search box.
         *   
         * If the user is not scrolling, this.selectedIndex == 0. We need 
         * to use the input as a regular search query. 
         * 
         */
        handleEnter() {
            // Even in mode:nft selectedIndex is 0, since the user is not 
            // scrolling down the autocomplete. 
            if (
                this.query.toLowerCase().trim().replace(/ /g,  '') === 'mode:nft') {
                this.isNftMode = true;
                this.query = '';
                return 
            } else {
                this.isNftMode = false;
            }
            // TODO(prashanth@): right now the user *has to select* from the 
            // drop down, meaning they can't type out "sloth bear" and hit 
            // enter. 
            if (
                this.selectedIndex >= 0 && 
                this.selectedIndex < this.suggestions.length) {
                    this.applyFilter(this.suggestions[this.selectedIndex])
                } 
        },
        clearSuggestions() {
            // TODO(prashanth@): attach @blur to this too. Currently the @blur 
            // clears the suggestion when a click on the dropdown occurs. We 
            // need to detect if the click is inside or outside the dropdown. 
            this.suggestions = [];
            this.selectedIndex = -1;
        },
        handleFocus() {
            if (!this.query.trim()) {
                // suggest keywords as the defaults 
                this.suggestions = [...this.keywordOptions];
            }
        },
        handleInput() {
            const input = this.query.toLowerCase();
            this.suggestions = [];

            if (input.startsWith('species:')) {
                const speciesSearch = input.replace('species:', '').trim();

                const startsWithResults = Object.keys(
                    this.data.autocomplete_species).filter(
                        species => species.startsWith(speciesSearch)
                    );

                const includesResults = Object.keys(
                    this.data.autocomplete_species).filter(
                        species => species.includes(
                            speciesSearch) && !species.startsWith(speciesSearch)
                    );

                this.suggestions = [
                    ...startsWithResults, 
                    ...includesResults].slice(0, 4);
            } else {
                this.suggestions = [...this.keywordOptions];
            }
        }, 
        areKeywords(suggestions) {
            return suggestions.every(
                suggestion => this.keywordOptions.includes(suggestion));
        },
        applyFilter(suggestion) {
            this.selectedIndex = -1;
            if (this.keywordOptions.includes(suggestion)) {
                // User has selected a keyword, copy it into the query bar
                this.query = suggestion;
                this.suggestions = [];

                // wait till dom redraw by vue before placing the caret in the 
                // search box
                this.$nextTick(() => {
                    const inputEl = this.$refs.searchInput; 
                    inputEl.focus()
                    inputEl.setSelectionRange(
                        suggestion.length, suggestion.length);
                });

            } else {
                const [key] = this.query.split(':');
                this.filters[key] = suggestion;
                // TODO(prashanth@): currently this just clears the query for 
                // convenience. Ideally we would retain the query + suggestion.
                // However at this point the query will contain eg: "species: s"
                // and the suggestion will contain "sloth bear", so some 
                // deduping is necessary to get it right.
                this.query = '';
                this.suggestions = [];

                if (key === 'species') {
                    // Step 1. Look up the sanctuaries for the species 
                    const sanctuaryNames = this.data.autocomplete_species[
                        this.filters[key]] || [];
                    
                    // Step 2. Find those sanctuaries in the full sanctuaries 
                    // list, and select the first one for display. 
                    this.filteredSanctuaries = this.data.sanctuaries_data.filter(
                        sanctuary => sanctuaryNames.includes(
                            sanctuary.sanctuary)
                    );
                    if (this.debugMode) {
                        this.selectedSanctuary = this.filteredSanctuaries[0];
                    }
                }
            }
        },
        selectSanctuary(sanctuary) {
            this.selectedSanctuary = sanctuary;
        },
        /* Badge handlers
         * 
         * Lookup the names of files, assume they're animal names, and compare 
         * them with the names of species in a sanctuary.
         */
        getFileName(imagePath) {
            return imagePath.split('/').pop().split('.').shift().toLowerCase();
        }, 
        getMatchingBadges(speciesList) {
            return this.nftImages.filter(
                image => {
                    const fileName = this.getFileName(image);
                    return speciesList.some(
                        species => species.toLowerCase().includes(fileName));
            });
        },
        handleBadgeClick(image) {
            this.selectedBadge = image;
            this.showPopup = true;
        },
        closePopup() {
            this.showPopup = false;
        },
        getPicForSelectedBadge() {
            return '/images/pics/' + this.selectedBadge.split('/').pop();
        },
        switchImage(index) {
            this.currentImageIndex = index;
        },
        getBadgeDelay(index) {
            if (index === 0) {
                return '1s';
            } else if (index > 0 && index <= 4) {
                return `${1 + Math.random() * 0.5}s`;
            } else {
                return `${1.5 + Math.random() * 2}s`;
            }
        }, 
        /* Plus button handlers */
        handleAddButton() {
            this.showAddSightingPopup = true;
        },
        closeAddSightingPopup() {
            this.showAddSightingPopup = false;
        },
        triggerFileUpload() {
            this.$refs.fileInput.click();
        },
        previewImage(event) {
            const file = event.target.files[0];
            if (file) {
                this.uploadedImage = URL.createObjectURL(file);
            }
        },
        handleConfirm() {
            if (this.uploadedImage) {
                this.userImage = '/images/nft/bearbull.png';
                this.closeAddSightingPopup();
                this.startBlurEffect();
            } 
        },
        startBlurEffect() {
            // Start blurring and remove it in 10s
            this.isLoading = true;
            setTimeout(() => {
                this.isLoading = false;
            }, 5000)
        },
        /* Nav tab handlers */
        setActiveTab(tab) {
            this.activeTab = tab;
        },
        /* Research papers */
        handleResearchClick(paper) {
            this.selectedPaper = paper;
            this.showFullPaperLink = false;
            this.startTyping(paper.title, paper.abstract);
        },
        startTyping(title, abstract) {
            this.typedTitle = "";
            this.typedAbstract = "";
            this.typeText(title, "typedTitle", () => {
                this.typeText(abstract, "typedAbstract", () => {
                    this.showFullPaperLink = true;
                });
            });
        },
        typeText(fullText, targetProperty, callback=null) {
            let index = 0;
            const typeChar = () => {
                if (index < fullText.length) {
                    this[targetProperty] += fullText.charAt(index);
                    index ++;
                    setTimeout(typeChar, this.typingSpeed);
                } else if (callback) {
                    callback();
                }
            };
            typeChar();
        },
        // Audio player 
        togglePlay() {
            const audio = this.$refs.audioPlayer;
            if (!this.isPlaying) {
                audio.play();
            } else {
                audio.pause();
            }
            this.isPlaying = !this.isPlaying;
        },
        /* NFT Mode handlers */
        setCurrentImage(index) {
            this.currentImageIndex = index;
            this.getTextContent();
        }, 
        updateVisibleImages() {
            const maxVisibleImages = 10;
            this.visibleImages = this.nftImages.slice(0, maxVisibleImages);
        },
        getPicImage() {
            return '/images/pics/' + this.nftImages[this.currentImageIndex].split('/').pop();
        },
        getTextContent() {
            const textPath = '/images/text/' + this.nftImages[
                this.currentImageIndex].split(
                    '/').pop().replace('.png', '.txt');
            console.log('Fetching text from path ', textPath);
            return fetch(textPath)
            .then(response => response.text())
            .then(text => {
                console.log('setting fetched text to ', text);
                this.fetchedText = text;
            })
            .catch(error => {
                console.log('Error fetching text: ', error);
                this.fetchedText = 'Error loading description';
            });
        },
    },
};
</script>

<style scoped>

.wrapper {
    background: url('http://localhost:8080/images/foxes.png') no-repeat;
    background-size: cover;
    background-attachment: fixed;
    height: 100vh;
    width: 100vw;
    display: flex;
    flex-direction: column;
    position: relative;
}

.search-section {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 20vh;
}

/* Search bar 
 * 
 * The search bar and icon are fixed as 2 individual elements alongside one 
 * another. They are only in the center of the search section because of 
 * justify/align/flex on the parent. 
 * 
 * The search-bar-wrappers helps keep them together even when they're squished. 
 * Otherwise the icon gets split to the next line. 
*/

.search-bar-wrapper {
    display: flex;
    align-items: center;
    position: relative;
}

.search-bar {
    flex: 1;
    border-radius: 0.5em 0 0 0.5em;    
    padding: 0.75em 1em;
    border: 0.1em solid #ccc;
    font-size: 1em;
    box-shadow: 0px 4px 8px rgba(0,0,0,0.1);
    transition: box-shadow 0.3s ease;
    width: 20em;

    background-color: rgba(255, 255, 255, 0.8);
    color: #316659;
}

.search-bar.no-bottom-radius {
    border-bottom-left-radius: 0;
}

.search-icon {
    background-color: #3D806F;
    color: white;
    border-radius: 0 0.5em 0.5em 0;
    padding: 0.75em 1em;
    border: 0.1em solid #ccc;
    font-size: 1em;
    cursor: pointer;
}

.search-icon:hover {
    background-color: #2F6A55;
}

.search-bar:focus {
    outline: none;
    box-shadow: 0px 6px 12px rgba(0, 0, 0, 0.2);
}

/* end search bar */

/* Autocomplete list drop down  
 * 
 * This uses the "position absolute" + "top 100%" pattern to stick the drop 
 * down list to the bottom of the parent element, which in this case is the 
 * search-section. 
 */

.search-container {
    position: relative;
}

.keyword-label {
    padding: 0.5em 1em;
    font-size: 0.8em;
    color: #888;
    text-align: left;
}

.autocomplete-dropdown {
    position: absolute;
    top: 100%;
    left: 0;
    width: calc(100% - 3.1em);
    border: 0.1em solid #ccc;
    box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
    z-index: 10; 
    border-radius: 0 0 1em 1em;

    background-color: rgba(255, 255, 255, 0.8);
    color: #316659;
}

.autocomplete-dropdown ul {
    list-style: none;
    margin: 0;
    padding: 0;
}

.autocomplete-dropdown li {
    padding: 0.5em 1em;
    cursor: pointer;
    font-size: 1em;
    text-align: left;
}

.autocomplete-dropdown li:hover {
    background-color: rgba(63, 123, 102, 0.1);
}

/* styling applied  to match hover, used for keyboard scroll */
.autocomplete-dropdown li.highlighted {
    background-color: rgba(63, 123, 102, 0.1);
}

/* end autocomplete list drop-down */

/* NFT Display */
.nft-carousel {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 80%;
    margin: 1em auto;
    overflow-x: auto;

}

.nft-image {
    max-width: 5em;
    max-height: 7em;
    object-fit: contain;
    margin: 0 1em;
    cursor: pointer;
}

.nft-info-box {
    display: flex;
    justify-content: space-around;
    align-items: center;
    background-color: rgba(255, 255, 255, 0.2);
    border-radius: 1em;
    width: 60vw;
    height: 40vh;
    margin: 2em auto;
}

.nft-info-left {
    flex: 1;
    display: flex;
    justify-content: center;
}

.nft-info-right {
    flex: 1;
    padding: 1em;
}

.nft-info-image {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
}

.nft-info-text {
    font-size: 1em;
    color: #dae4e1;
    overflow-y: auto;
}

/* End  NFT Display */

/* Results section  
 * 
 * The results are displayed as a scrollable list via overflow-y: Auto. The 
 * the rest of the results section is kept intentionally simple. 
 *
 * When a result is clicked, the corresponding badge and sanctuary info is 
 * displayed on the right hand side split container. 
*/
.joined-box {
    display: flex;
    width: 80%;
    margin: 0 auto;
    background-color: rgba(56, 68, 84, 0.6);
    border-radius: 1em;
    padding: 1em;
    position: relative; 
    color: #a8d5ba;
    max-height: 70vh;
}

.results-box {
    width: 20%;
    overflow-y: auto;
}

.sanctuary-row {
    padding: 1em 0;
    border-bottom: 0.1em solid rgba(255, 255, 255, 0.1);
}

.sanctuary-name {
    font-size: 1.2em;
    font-weight: bold;
    text-align: left;
}

.vertical-line {
    width: 1px;
    background-color: rgba(255, 255, 255, 0.1);
    height: 100%;
}

/* Sanctuary info section (right half of the joined-box) 
 *
 * This section has an effect that uses vue's transition feature.
 */

.fade-slide-enter-active {
  transition: opacity 2s ease, transform 2s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(20px); /* Slide effect */
}

.sanctuary-info-box {
    width: 80%;
    padding: 1em;
    border-radius: 1em;
    overflow-y: auto;
}

.title-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: relative;
}

.tab-bar {
    position: absolute;
    bottom: 0%;
    right: 0%;
}

.tab {
    padding: 0.5em 1em;
    cursor: pointer;
    font-family: 'VT323', monospace;
    color: #A8D5BA;
    background-color: rgba(56, 68, 84, 0.0);
    /* background-color: #1e1f25; */
    border: 1px solid #444;
    border-radius: 8px 8px 0 0;
}

.tab.active {
  /* background-color: #444; */
  /* background-color: #1e1f25; */
  background-color: #1e1f25;
  font-weight: bold;
}

.sanctuary-title {
    font-size: 2em;
    font-weight: bold;
    text-align: left;
    font-family: 'VT323', monospace;
}

.horizontal-line {
    border: none;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    /* margin: 0.5em 0; */
    margin-top: 0;
}

/* Two-column layout for sanctuary info */
.info-container {
    display: flex;
    justify-content: space-between;
}


/* Left display: badges and text info */
.info-left {
    width: 50%;
    font-size: 1.1em;
}

.vertical-divider {
    width: 1px;
    background-color: rgba(255, 255, 255, 0.1);
    height: 100%;
    margin: 0 1em; 
    height: auto;
}

.stylised-text {
    font-family: 'VT323', monospace;
    font-size: 1.2em;
    color: #5bd6ab;
    margin-top: 1em;
    text-align: left;
}


/* Badge row display */
.badges {
    margin-top: 1em;
    display: flex;
    flex-wrap: wrap;
    gap: 0em;
}

.badge {
    width: 50px; 
    height: 50px;
    border-radius: 50%;
    overflow: hidden;
    display: inline-block;
    position: relative;
    box-shadow: 0px 0px 15px rgba(0, 0, 0, 0.5);
    padding: 0.3em;
    background: linear-gradient(145deg, #FFD700, #B8860B);
    /* TODO(prashanth@): apply a red circle for endangered? (2px solid brown) */
    border: 5px solid black;
    object-fit: cover;
    cursor: pointer;

    animation: popOut 1s ease-in-out forwards;
    opacity: 0;
} 

.user-badge {
    /* Unblurring animation */
    transition: transform 0.2s, filter 3s ease;
}

.user-badge.blurred {
    filter: blur(5px);
}

.user-badge:not(.blurred):hover {
  transform: scale(1.1); /* Slight scale-up on hover after unblur */
}

/* Badge popout animaion
 * 
 * We intentionally overshoot at 50% to give the popping out effect. 
 * This is added to the .badge class above, but an `animation-delay` 
 * style is added via javascript through the mounted() handlers. 
 */
@keyframes popOut {
    0% {
        opacity: 0;
        transform: scale(0);
    }
    50% {
        opacity: 1;
        transform: scale(1.1);
    }
    100% {
        opacity: 1;
        transform: scale(1);
    }
}

/* The last badge (the plus badge) has 2 unique features
 * 
 * 1. A shine effect 
 * 
 * This is achieved by placing an element right before it 
 * (via position: absolute). Even though this element's height and width 
 * overlap with surrounding elements it's hidden with the overflow.  
 * 
 * 2. A tooltip: TODO(prashanth@): implement
 */
.plus-badge-container {
    position: relative;
    display: inline-block;
    overflow: hidden;
    cursor: pointer;
    border-radius: 50%;
}

.plus-badge {
    position: relative;
    /* Ensure the plus badge itself is never occluded */
    z-index: 1;
}

.plus-badge-container::before {
    /* Content is mandatory for ::before */
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 200%;
    height: 100%;
    background: linear-gradient(120deg, rgba(0, 123, 255, 0.3), rgba(135, 206, 250, 0.5), rgba(0, 123, 255, 0.3));
    transform: skewX(-45deg);
    transition: transform 0.2s ease-in-out;
    opacity: 0;
    border-radius: 50%;
    z-index: 2;
    pointer-events: none;
}

.plus-badge-container:hover::before,
.plus-badge-container::before {
    opacity: 1;
    animation: water-shine 5s infinite ease-in-out;
}

@keyframes water-shine {
    0% {
        transform: translateX(-200%) skewX(-45deg);
        opacity: 0;
    }
    50% { 
        /* Shine moves across the middle */
        transform: translateX(0%) skewX(-45deg);  
        opacity: 1;
    }
    100% {
        /* Shine exits far right */
        transform: translateX(200%) skewX(-45deg);  
        opacity: 0;
    }
}
/* End shine effect */

/* End plus badge */

/* Right display: map data */
.info-right {
    width: 50%; 
    height: 100%;
    padding: 1.5em;
    display: flex;
    justify-content: center;
    align-items: center;
    position: relative;
    overflow-y: hidden;
}

.map-container {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    height: 100%;
    margin-right: 50px;
}

.map-image {
    width: 90%;
    height: auto;
    object-fit: contain;
    opacity: 0.8;
}

/* End Results section */

/* Badge popup 
 * 
 * popup-overlay: is the blurry background.
 * popup-card: is the container for both the image and the text.
 * popup-image: is the left half of popup-card, the image.
 * popup-description: is the right half of the popup-card, the text. 
 */

.popup-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(0, 0, 0, 0.6);
    display: flex;
    justify-content: center;
    align-items: center;
    backdrop-filter: blur(10px);
    z-index: 1000;
}

.popup-card {
    display: flex;
    width: 50%;
    height: 50vh;
    border-radius: 15px;
    overflow: hidden;
    position: relative;
    box-shadow: 0px 0px 20px rgba(0, 0, 0, 0.5);
}

.popup-image-container {
    position: relative;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    max-width: 50%;
    height: 100%;
}

.popup-image {
    object-fit: contain;
    height: auto;
    /* Reduce to 50% to get consistent borders.
     * 
     * We don't know the dimension of the user uploaded images. Reducing 
     * this width could avoid cropping.
     */
    width: 100%;
}

/* Image nav dots for popup card */
.image-nav {
    display: flex;
    justify-content: center;
    align-items: center;
    position: absolute;
    bottom: 10px;
    left: 50%;
    gap: 10px;
    transform: translateX(-50%);
}

.nav-dot {
    background-color: rgba(255, 255, 255, 0.5);
    border-radius: 50%;
    cursor: pointer;
    transition: background-color 0.3s;
    width: 10px; 
    height: 10px;
}

.nav-dot.active {
    background-color: rgba(255, 255, 255, 1);
}

.nav-dot:hover {
    background-color: rgba(255, 255, 255, 0.8);
}

/* End image nav dots */

.popup-description {
    flex: 1;
    background-color: #0C0D10;
    color: white;
    padding: 2em;
    display: flex;
    flex-direction: column;
    text-align: left;
    height: 100%;
    box-sizing: border-box;
}

.popup-description-topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    font-weight: bold;
    color: #B0B0B0;
}

.popup-description-username {
    display: inline-flex;
    align-items: center;
}

.popup-description-content {
    margin-top: 1em;
    font-size: calc(1vw + 0.5em);
    line-height: 1.5em;
    word-wrap: break-word;
    flex-grow: 1;
    overflow-y: auto;
}

.popup-description-content p {
    margin: 0;
    padding: 0;
}

.popup-close {
    position: absolute;
    top: 8px;
    right: 15px;
    z-index: 10;

    font-size: 1.5em;
    color: #B0B0B0;
    cursor: pointer;
    background: none;
    border: none;
    padding: 0;
    transition: color 0.3s ease;
    border-radius: 50%;
    display: flex;
}

.popup-close:hover {
    color: #fff;
}

/* File upload popup for plus button 
 * 
 * This popup uses the same styling as .popup-overlay.
 */
.add-sighting-popup {
    background-color: #1e1f25;
    padding: 2em;
    border-radius: 10px;
    width: 400px;
    display: flex;
    flex-direction: column;
    gap: 1.5em;
    position: relative;
}

.popup-text-input {
    padding: 0.75em;
    border-radius: 5px;
    border: none;
    background-color: #2b2c35;
    color: white;
    font-size: 1em;
}

.popup-text-input::placeholder {
    color: #888;
}

/* File upload box */
.file-upload-box {
    border: 2px dashed #888;
    padding: 2em;
    border-radius: 5px;
    text-align: center;
    color: #888;
    cursor: pointer;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

.upload-text {
    font-size: 1em;
}

.file-input {
    display: none;
}

.file-upload-box:hover {
    border-color: #ccc;
}

/* Display uploaded image and submit */
.uploaded-image {
    width: 100%;
    max-width: 100%;
    border-radius: 8px;
}

.confirm-button {
    background-color: #1e1f25;
    font-family: 'VT323', monospace;
    border: none;
    color: #5bd6ab;
    border-radius: 8px;
    padding: 0.75em;
    cursor: pointer;
    font-size: 1.2em;
    margin: 0px;
    padding: 0px;
}

/* NFT mode badging */
.badge-box {
    display: grid;
    grid-template-columns: repeat(5, auto);
    grid-template-rows: auto;
    gap: 0px;
    justify-content: center; 
    align-items: center;
}

/* Experiments */


/* Research papers tab
 * 
 * This appears as a tab in the results::map section. It's placed here for 
 * convenience.
 * 
 * The main layout comprises of a stack of VHS tapes, followed by a 
 * computer screen.
 */
.vhs-stack {
    position: relative;
    /* Width of the VHS tapes */
    width: 500px; 
    margin: 0 auto; 
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
}

.vhs-tape {
    position: relative;
    background-color: #000;
    color: white;
    /* Unequal padding so we have extra 20px on the left */
    padding: 0 10px 0 30px;
    /* Fixed height for the VHS tape */
    height: 60px; 
    width: 100%;
    border: 2px solid #EDB883; 
    border-radius: 4px;
    display: flex;
    align-items: center;
    box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.6);
    /* Jitter on X-axis */
    transform: translateX(calc(var(--offset) * 5px));
    overflow: hidden;

    background:
        radial-gradient(circle at left, rgba(0, 0, 0, 0.4), transparent 80%),
        radial-gradient(circle at right, rgba(0, 0, 0, 0.4), transparent 80%),
        linear-gradient(to right, rgba(255, 255, 255, 0.1), transparent 30%, transparent 70%, rgba(255, 255, 255, 0.1));
    
    animation: slideUp 0.5s ease-in-out forwards; 
    opacity: 0;
}

@keyframes slideUp {
    0% {
        opacity: 0;
        transform: translateY(20px);
    }
    100% {
        opacity: 1;
        transform: translateY(0);
    }
}

.vhs-tape:nth-child(1) {
    animation-delay: 0s;
}

.vhs-tape:nth-child(2) {
    animation-delay: 0.1s;
}

.vhs-tape:nth-child(3) {
    animation-delay: 0.2s;
}

.vhs-tape:nth-child(4) {
    animation-delay: 0.3s;
}

.vhs-tape:nth-child(5) {
    animation-delay: 0.4s;
}

/* vhs-tape + vhs-label is how we control the background images of each tape */
.vhs-tape:nth-child(1) .vhs-label {
    background-image: url('http://localhost:8080/images/vhs/vhs1.png');
}

.vhs-tape:nth-child(2) .vhs-label {
    background-image: url('http://localhost:8080/images/vhs/vhs2.png');
}

.vhs-tape:nth-child(3) .vhs-label {
    background-image: url('http://localhost:8080/images/vhs/vhs3.png');
}

.vhs-tape:nth-child(4) .vhs-label {
    background-image: url('http://localhost:8080/images/vhs/vhs4.png');
}

.vhs-tape:nth-child(5) .vhs-label {
    background-image: url('http://localhost:8080/images/vhs/vhs5.png');
}

/* This adds the tiny square that's indented in most tapes */
.vhs-tape::before {
    content: '';
    position: absolute;
    left: 20px;
    width: 25px;
    height: 25px;
    background-color: #000;
    box-shadow: 1px 1px 3px rgba(129, 128, 128, 0.6);
    border-radius: 1px;
}

/* Hover Effect for Interaction */
.vhs-tape:hover {
    /* No change to the tape movement */
    transform: translateX(calc(var(--offset) * 5px)); 
}

/* Label section with background image */
.vhs-label {
    position: relative;
    background-size: 95% 100%;
    background-position: center;
    background-repeat: no-repeat;
    padding: 0.5em 1em;
    font-family: 'Courier Prime', monospace;
    flex-grow: 1;

    display: flex;
    align-items: center;
    overflow: hidden;
    justify-content: flex-end;
}

/* White "sticker" for the title */
.vhs-title-sticker {
    /* White-ish sticker with slight transparency */
    background-color: rgba(255, 255, 255, 0.9); 
    padding: 0.2em 0.5em;
    border-radius: 2px;
    /* Slight shadow for sticker effect */
    box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.5); 
    font-weight: bold;
    /* Dark color for the title */
    color: #333; 
    /* Ensure title fits within the tape */
    max-width: 90%; 
    white-space: nowrap;
    overflow: hidden;
    /* Ellipsis for long titles */
    text-overflow: ellipsis; 
    margin-left: 10px;
    overflow: hidden;
    font-size: 1em;
}

.vhs-tape:hover .vhs-title-sticker {
    /* Move the sticker to the left */
    transform: translateX(-10px); 
    box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.4);
    animation: moveAndReturn 0.6s ease-in-out;
}

@keyframes moveAndReturn {
    0% {
        transform: translateX(0);
    }
    50% {
        transform: translateX(-10px);
    }
    100% {
        transform: translateX(0);
    }
}


/* End VHS styling */

/* Compute screen: Abstract Section Styling */
.abstract-section a {
  font-weight: bold;
  text-decoration: none;
  color: #08aed8;
  font-size: 1em;
}

.tv-screen {
    /* Dark gray background for TV screen effect */
    background-color: #333; 
    width: 100%;
    /* Adjust based on your layout */
    height: 170px; 
    margin-bottom: 1em;
    padding: 1em;
    color: #F2E7D5; 
    border-radius: 10px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    /* Initially hidden */
    opacity: 0; 
    /* Animation to "turn on" the Computer screen */
    animation: screenOn 1s ease-in forwards; 

    /* Retro border styling */
    border: 0.5em solid #6F597F;
    box-shadow: 
    /* Inner shadow for screen depth */
    inset 0 0 5px #000, 
    /* Outer shadow for the monitor box effect */
    0 0 20px rgba(0, 0, 0, 0.8), 
    /* Faint glowing effect */
    0 0 0.5em #6F597F, 
    /* Inside glow for retro screen effect */
    0 0 1em #6F597F inset,
    /* Extra shadow for depth */
    0.25em 0.25em 1em rgba(0, 0, 0, 0.5); 
}

/* Animation to "turn on" the Computer screen */
@keyframes screenOn {
  0% {
    opacity: 0;
    /* Starts off as a thin line (Computer turning on) */
    transform: scaleY(0); 
  }
  50% {
    opacity: 0.5;
    /* Overshoot a little for a bounce effect */
    transform: scaleY(1.05); 
  }
  100% {
    opacity: 1;
    /* Normal scale */
    transform: scaleY(1); 
  }
}

/* Audio player styling */
.play-button {
    margin-left: 10px;
    background-color: transparent;
    border: none;
    cursor: pointer;
    font-size: 1.2em;
}

.play-icon {
  width: 20px; /* Adjust size of the play icon */
  height: 20px;
  padding-top: 7px;
}

.play-button:hover {
    color: #08aed8;
}

.paper-actions {
    display: flex;
    align-items: center;
}


</style>

