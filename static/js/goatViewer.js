function GoatViewer(myGoats, numRows, goatsPerRow) {
    const GOATS_PER_PAGE = numRows * goatsPerRow;

    this.updateCards = (goats) => {
        $('#cards').empty();

        for (let row = 0; row < numRows; row++) {
            const deck = $('<div class="card-deck"></div>');

            for (let col = 0; col < goatsPerRow; col++) {
                const index = row * goatsPerRow + col;
                if (index < goats.length) {
                    const goat = goats[row * goatsPerRow + col];

                    const card = $(`
                        <div class="card ${myGoats || goat.adopted < 0 ? '' : 'adopted'}">
                            <img class="card-img-top" src="/static/img/goats/${goat.image}">
                            <div class="card-body">
                                <h5 class="card-title">${goat.name}</h5>
                                <p class="card-text">${goat.age} years old</p>
                                <button class="adopt-button btn btn-primary">
                                    ${myGoats ? 'Unadopt' : 'Adopt'}
                                </button>
                            </div>
                        </div>
                    `);

                    $(card).find('.adopt-button').on('click', _ => {
                        if (myGoats)
                            this.unadopt(goat);
                        else
                            this.adopt(goat);
                    });

                    $(deck).append(card);
                } else {

                    const card = $(`
                        <div class="card">
                        </div>
                    `);
                    $(deck).append(card);

                }
            }

            $('#cards').append(deck);
        }
    }

    const createPageLink = (text, toPage, active, disabled) => {
        const link = $(`
            <li class="page-item">
                <a class="page-link">${text}</a>
            </li>
        `);
        $(link).find('.page-link').on('click', _ => {
            this.currentPage = toPage;
            this.load();
        });
        if (active)
            link.addClass('active');
        if (disabled)
            link.addClass('disabled');
        return link;
    }

    this.currentPage = 1;

    this.updatePagination = (total) => {
        let pages = Math.ceil(total / GOATS_PER_PAGE);
        $('#paginator').empty().append(
            createPageLink('Previous', this.currentPage - 1, false, this.currentPage == 1)
        );
        for (let page = 1; page <= pages; page++)
            $('#paginator').append(
                createPageLink(page, page, page == this.currentPage, false)
            );
        $('#paginator').append(
            createPageLink('Next', this.currentPage + 1, false, this.currentPage == pages)
        );
    }

    this.update = (data) => {
        this.updateCards(data.goats);
        this.updatePagination(data.total);
    }

    this.load = () => {
        $.get(myGoats ? '/api/my_goats' : '/api/get_goats', {
            n: GOATS_PER_PAGE,
            offset: (this.currentPage - 1) * GOATS_PER_PAGE
        }, (data) => {
            this.update(data);
        });
    }

    this.adopt = (goat) => {
        $.post('/api/adopt_goat', {
            goat_id: goat.id,
            n: GOATS_PER_PAGE,
            offset: (this.currentPage - 1) * GOATS_PER_PAGE
        }, (data) => {
            this.update(data);
        });
    }

    this.unadopt = (goat) => {
        $.post('/api/unadopt_goat', {
            goat_id: goat.id,
            n: GOATS_PER_PAGE,
            offset: (this.currentPage - 1) * GOATS_PER_PAGE
        }, (data) => {
            this.update(data);
        });
    }
}
