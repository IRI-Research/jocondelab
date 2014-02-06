/* -*- coding: utf-8 -*- 
*
* Copyright Institut de Recherche et d'Innovation © 2014
*
* contact@iri.centrepompidou.fr
*
* Ce code a été développé pour un premier usage dans JocondeLab, projet du 
* ministère de la culture et de la communication visant à expérimenter la
* recherche sémantique dans la base Joconde
* (http://jocondelab.iri-research.org/).
*
* Ce logiciel est régi par la licence CeCILL-C soumise au droit français et
* respectant les principes de diffusion des logiciels libres. Vous pouvez
* utiliser, modifier et/ou redistribuer ce programme sous les conditions
* de la licence CeCILL-C telle que diffusée par le CEA, le CNRS et l'INRIA 
* sur le site "http://www.cecill.info".
*
* En contrepartie de l'accessibilité au code source et des droits de copie,
* de modification et de redistribution accordés par cette licence, il n'est
* offert aux utilisateurs qu'une garantie limitée.  Pour les mêmes raisons,
* seule une responsabilité restreinte pèse sur l'auteur du programme,  le
* titulaire des droits patrimoniaux et les concédants successifs.
*
* A cet égard  l'attention de l'utilisateur est attirée sur les risques
* associés au chargement,  à l'utilisation,  à la modification et/ou au
* développement et à la reproduction du logiciel par l'utilisateur étant 
* donné sa spécificité de logiciel libre, qui peut le rendre complexe à 
* manipuler et qui le réserve donc à des développeurs et des professionnels
* avertis possédant  des  connaissances  informatiques approfondies.  Les
* utilisateurs sont donc invités à charger  et  tester  l'adéquation  du
* logiciel à leurs besoins dans des conditions permettant d'assurer la
* sécurité de leurs systèmes et ou de leurs données et, plus généralement, 
* à l'utiliser et l'exploiter dans les mêmes conditions de sécurité. 
*
* Le fait que vous puissiez accéder à cet en-tête signifie que vous avez 
* pris connaissance de la licence CeCILL-C, et que vous en avez accepté les
* termes.
*
*/

/* Image load events may be triggered before jQuery is loaded.
 * Here we bind temporary functions to the Window namespace */

(function() {
    
    function tmpBind(property) {
        window[property] = function() {
            var arglist = Array.prototype.slice.call(arguments);
            setTimeout(function() {
                window[property].apply(window, arglist);
            }, 500);
        };
    }
    
    var propsToBind = [ "onWikiImageLoad", "onWikiImageError", "onResultImageError" ];
    for (var i = 0; i < propsToBind.length; i++) {
        tmpBind(propsToBind[i]);
    }
    
})();

$(function() {
    
    var lang = $("html").attr("lang").substr(0,2) || "fr";
    
    /* SEARCH TAG-IT */
   
    var $searchInput = $(".search-input"),
        originalValue = $searchInput.val(),
        allowSubmit = false,
        uri_cache = window.uri_cache || {};
    
    function submitIfChanged(e, ui) {
        var val = $searchInput.val();
        if (allowSubmit && val && val !== originalValue) {
            var labels_to_look = val.split(";"),
                dbpedia_uris = [];
                _(labels_to_look).each(function(lbl) {
                    var uri = uri_cache[lbl.toLowerCase()];
                    if (uri) {
                        dbpedia_uris.push(uri);
                    }
                });
            if (dbpedia_uris.length === labels_to_look.length) {
                $searchInput.val(dbpedia_uris.join(";")).attr("name", "dbpedia_uri");
            }
            $(".search-form").submit();
        }
    }
    
    $searchInput.tagit({
        autocomplete: {
            source: urls.ajax_terms,
            minLength: (lang === "ja" || lang == "zh") ? 1 : 2,
            focus: function(e, ui) {
            	if(window.innerWidth>559){
                    showDbpediaBox(ui.item.dbpedia_uri);
                    setDbpediaBoxAnchor({type: "dom", selector: $(e.target).autocomplete("widget"), positioning: "side"});
                }
            },
            response: function(e, ui) {
                _(ui.content).each(function(c) {
                    uri_cache[c.label.toLowerCase()] = c.dbpedia_uri;
                });
            }
        },
        allowSpaces: true,
        afterTagAdded : submitIfChanged,
        afterTagRemoved: submitIfChanged,
        singleFieldDelimiter: ";"
    });
    allowSubmit = true;
    
    /* END SEARCH TAG-IT */
    
    /* DBPEDIA OVERLAY */
    
    var sparqlTpl = _.template(
            'select distinct * where { '
            + 'OPTIONAL { <<%= uri %>> rdfs:label ?l FILTER( langMatches( lang(?l), "<%- lang %>" ) ) }. '
            + 'OPTIONAL { <<%= uri %>> dbpedia-owl:thumbnail ?t }. '
            + 'OPTIONAL { <<%= uri %>> dbpedia-owl:abstract ?a FILTER( langMatches( lang(?a), "<%- lang %>" ) ) }. '
            + 'OPTIONAL { <<%= uri %>> dbpedia-owl:wikiPageRedirects ?r }. '
            + 'OPTIONAL { ?r rdfs:label ?lr FILTER( langMatches( lang(?lr), "<%- lang %>" ) ) }. '
            + 'OPTIONAL { ?r dbpedia-owl:thumbnail ?tr }. '
            + 'OPTIONAL { ?r dbpedia-owl:abstract ?ar FILTER( langMatches( lang(?ar), "<%- lang %>" ) ) }. '
            + '}'
        ),
        $overlay = $(".dbpedia-overlay"),
        hovering = null,
        anchor = null,
        $win = $(window),
        dbpediaCache = {},
        $overlayImg = $overlay.find("img"),
        $h2 = $overlay.find("h2"),
        $abstract = $overlay.find(".dbpedia-abstract"),
        $source = $overlay.find(".dbpedia-source a");
    
    function setDbpediaBoxAnchor(a) {
        anchor = a || null;
        if (anchor) {
            recentreDbpediaBox();
        }
    }
    
    function recentreDbpediaBox() {
        if (!anchor) { return; }
        var ovw = $overlay.outerWidth(),
            ovh = $overlay.outerHeight(),
            refbox;
        switch (anchor.type) {
            case "dom":
                var $refdiv = anchor.selector,
                    refoff = $refdiv.offset(),
                    refw = $refdiv.outerWidth(),
                    refh = $refdiv.outerHeight(),
                    refx = refoff.left,
                    refy = refoff.top;
                refbox = { left: refx, right: refx + refw, top: refy, bottom: refy + refh };
            break;
            case "box":
                refbox = anchor.box;
            break;
            case "callback":
                refbox = anchor.callback();
            break;
        }
        if (!refbox) { return; }
        if (!refbox.right) { refbox.right = refbox.left; }
        if (!refbox.bottom) { refbox.bottom = refbox.top; }
        refbox.hcentre = (refbox.left + refbox.right) / 2;
        switch (anchor.positioning) {
            case "side":
                var showLeft = (refbox.right + ovw) > $win.width();
                css = { left: showLeft ? (refbox.left - ovw) : (refbox.right), top: refbox.top };
            break;
            case "bottom":
                css = { left: refbox.hcentre - ovw / 2, top: refbox.bottom };
            break;
            case "vertical":
            default:
                var showAbove = (refbox.bottom + ovh) > ($win.height() + $win.scrollTop());
                css = { left: refbox.hcentre - ovw / 2, top: showAbove ? refbox.top - ovh : refbox.bottom };
        }
        if (css) {
            css.left = Math.max(5, Math.min($win.width() - ovw - 5, css.left));
            $overlay.css(css);
        }
    }
        
    function showDbpediaBox(dbpediaUri) {
        if (!dbpediaUri) {
            return;
        }
        hovering = dbpediaUri;
        $overlay.hide();
        $overlayImg.attr("src","");
        var uriData = dbpediaCache[dbpediaUri];
        if (!uriData) {
            getUriData(dbpediaUri);
            return;
        }
        $overlay.show().attr("data-dbpedia-uri", dbpediaUri);
        if (uriData.t || uriData.tr) {
            $overlayImg.attr("src",uriData.t || uriData.tr).show();
        } else {
            $overlayImg.hide();
        }
        var label = uriData.l || uriData.lr || "",
            wkUrl = "http://" + lang + ".wikipedia.org/";
        if (label) {
            wkUrl += "wiki/" + encodeURI(label.replace(/ /g,'_'));
        } 
        $h2.text((uriData.l && uriData.lr) ? (uriData.l + " → " + uriData.lr) : label);
        $abstract.text((uriData.a || uriData.ar || "").replace(/^(.{240,260})\s.+$/,'$1…').substr(0,261));
        $source.attr("href", wkUrl);
        recentreDbpediaBox();
    }
    
    function getUriData(dbpediaUri) {
        if (typeof dbpediaCache[dbpediaUri] !== "undefined") {
            return;
        }
        var sparqlEndpoint = dbpediaUri.replace(/\/resource\/.*$/,'/sparql'),
            query = sparqlTpl({uri: decodeURI(dbpediaUri), lang: lang});
        dbpediaCache[dbpediaUri] = false;
        $.getJSON(sparqlEndpoint, {
            query: query,
            format: "application/sparql-results+json"
        }, function(data) {
            if (!data.results || !data.results.bindings || !data.results.bindings.length) {
                return;
            }
            var res = data.results.bindings[0], cacheData = {};
            for (var k in res) {
                if (res.hasOwnProperty(k)) {
                    cacheData[k] = res[k].value;
                }
            }
            dbpediaCache[dbpediaUri] = cacheData;
            if (hovering === dbpediaUri) {
                showDbpediaBox(dbpediaUri);
            }
        });
    }
        
    function hideDbpediaBox() {
        hovering = null;
        setTimeout(function() {
            if (!hovering) {
                $overlay.hide();
                setDbpediaBoxAnchor();
                deferredRemovePopin();
            }
        }, 0);
    }
    
    function bindDbpediaBox(selector, defaultUri) {
        var $sel = $(selector);
        $sel.off("mouseenter mouseleave");
        $sel.mouseenter(function(e) {
            var $this = $(this);
            setDbpediaBoxAnchor({ selector: $this, type: "dom", positioning: "vertical" });
            var dbpediaUri = $this.attr("data-dbpedia-uri") || defaultUri;
            if (!dbpediaUri || dbpediaUri === "None") {
                return;
            }
            showDbpediaBox(dbpediaUri);
        });
        $sel.mouseleave(hideDbpediaBox);
    }
        
    $overlay.hover(function() {
        var $this = $(this),
            dbpediaUri = $this.attr("data-dbpedia-uri");
        if (dbpediaUri) {
            hovering = dbpediaUri;
        }
    }, hideDbpediaBox);
    
    $overlay.find(".dbpedia-close").click(function() {
        hideDbpediaBox();
        return false;
    });
    
    window.dbpediaBox = {
        bind: bindDbpediaBox,
        hide: hideDbpediaBox,
        show: showDbpediaBox,
        setAnchor: setDbpediaBoxAnchor,
        recentre: recentreDbpediaBox
    };
    
    /* END DBPEDIA OVERLAY MANAGEMENT */
   
    /* NOTICE LIST MANAGEMENT */
   
    var gridsize = 160,
        $popin = null,
        $results = $(".results"),
        hoverPopin = false;
    
    function removePopin() {
        if ($popin) {
            $(".notice-item").removeClass("notice-hover");
            $popin = null;
        }
    }  
    
    function deferredRemovePopin() {
        window.setTimeout(function() {
            if (!hoverPopin) {
                removePopin();
            }
        }, 0);
    }
            
    function adaptGrid() {
        var $tblist = $(".notice-list");
        if ($tblist.length) {
            gridsize = $(".notice-item").width() || 160;
            var outerw = $results.width(),
                delta = outerw % gridsize,
                innerw = outerw - delta,
                p = Math.floor(delta/2);
            $tblist.css({
                padding: "0 " + p + "px"
            });
            var $wikinfo = $(".wiki-info");
            if ($wikinfo.length) {
                var wkw = Math.min(3*gridsize, innerw),
                    wkh = 2*gridsize;
                $wikinfo.css({
                    width: wkw + "px",
                    height: wkh + "px"
                });
                $wikinfo.find(".wiki-info-image").css({
                    "max-width": (wkw / 2 - 10) + "px",
                    "max-height": wkh - 20
                });
            }
        }
        throttledCheckSizes();
    }
    
    function checkSizes() {
        var notloaded = false;
        $(".notice-item").each(function() {
            var $this = $(this),
                $nc = $(this).find(".notice-contents"),
                $img = $(this).find(".notice-image"),
                $md = $(this).find(".notice-metadata"),
                img = $img[0],
                iw = img.width,
                ih = img.height;
            if (!img.complete || iw < 30 || ih < 30) {
                notloaded = true;
                return;
            }
            var scale = Math.min(2, gridsize / Math.min(iw, ih)),
                nw = scale * iw,
                nh = scale * ih,
                ww = $win.width(),
                isleft = ($this.offset().left + gridsize / 2 < ww / 2),
                isfull = (nw > ww - 300);
            $img.css({
                width: nw + "px",
                height: nh + "px",
                float: isleft ? "left": "right"
            });
            $md.css({
                "margin-left" : (isleft && !isfull) ? nw + 10 : 0,
                "margin-right" : (!isleft && !isfull) ? nw + 10 : 0
            });
            $nc.css({
                left: isleft ? "0" : "",
                right: isleft ? "" : "0",
                width: isfull ? nw : (nw + 250),
                "margin-top": ((gridsize - nh) / 3 - 10) + "px",
                "margin-left": isleft ? ((gridsize - nw) / 2 - 10) + "px" : 0,
                "margin-right": isleft ? 0 : ((gridsize - nw) / 2 - 10) + "px"
            });
        });
        if (notloaded) {
            setTimeout(throttledCheckSizes, 800);
        }
    }
    
    var throttledCheckSizes = _(checkSizes).throttle(500);
    
    window.bindResultsMouseover = function() {
        var $items = $(".notice-item");
        $items.off("mouseenter mouseover");
        $items.mouseenter(function() {
            var $this = $(this);
            hoverPopin = true;
            if ($popin && $popin === $this) {
                return;
            }
            removePopin();
            if (!$this.find(".notice-image")[0].width) {
                return;
            }
            $popin = $this;
            $this.addClass("notice-hover");
        });
        $items.mouseleave(function() {
            hoverPopin = false;
            if ($overlay.is(":hidden")) {
                deferredRemovePopin();
            }
        });
        bindDbpediaBox($items.find(".notice-term a"));
        adaptGrid();
    };
    
    window.onResultImageError = function(img) {
        img.src = urls.img_if_404;
        $(img).css("background-image", $(".header-wrapper").css("background-image"));
        throttledCheckSizes();
    };
    
    /* END NOTICE LIST MANAGEMENT */
    
    /* AJAX SCROLL LOAD */
    
    var max_scroll_pages = 3, currentpage;
    
    function loadMorePages(query) {
        $(".load-more").hide();
        $win.off("scroll.ajaxload");
        $(".notice-list").empty();
        $(".loading-please-wait").show();
        currentpage++;
        $(".notice-list").attr("data-current-page", currentpage);
        $.ajax({
            url: urls.ajax_search,
            data: _({ page: currentpage }).extend(query),
            dataType: "html",
            success: function(html) {
                $(".notice-list").html(html);
                bindResultsMouseover();
                $(".loading-please-wait").hide();
                scrollLoad(query);
                // We check if last element has attribute "last page" and, if so, we cancel loading next page
                var attr = $(".notice-list").children().last().attr('data-last-notice');
                if(typeof attr !== 'undefined' && attr !== false){
            		$win.off("scroll.ajaxload");
                    $(".load-more").hide();
                    $(".loading-please-wait").hide();
            		window.stopTimeOut();
                }
                else{
                	// Enable load page when scroll not available
                    startTimeOut();
                }
            }
        });
    }
    
    window.scrollLoad = function(query) {
        currentpage = parseInt($(".notice-list").attr("data-current-page"));
        var loadingnext = false,
            page_count = parseInt($(".notice-list").attr("data-page-count")),
            max_page = Math.min(currentpage + max_scroll_pages, page_count);
        
        $(".load-more").hide().off("click").click(function() {
            loadMorePages(query);
            return false;
        });
        $win.on("scroll.ajaxload", function() {
            if (loadingnext || currentpage >= max_page) {
                return;
            }
            var $datablock = $(".notice-list"),
                dbo = $datablock.offset();
            if (!dbo) {
                return;
            }
            var winbottom = $win.scrollTop() + $win.height(),
                databottom = dbo.top + $datablock.height();
            
            if (winbottom >= databottom && !loadingnext) {
                loadingnext = true;
                $(".loading-please-wait").show();
                $.ajax({
                    url: urls.ajax_search,
                    data: _({ page: ++currentpage }).extend(query),
                    dataType: "html",
                    success: function(html) {
                    	var last_page = false;
                    	if(html.trim()!=""){
                    		$datablock.append(html);
                            loadingnext = false;
                            bindResultsMouseover();
                            $(".loading-please-wait").hide();
                            if (currentpage >= max_page && currentpage < page_count) {
                                $(".load-more").show();
                            }
                            // We check if last element has attribute "last page" and, if so, we cancel loading next page
                            var attr = $datablock.children().last().attr('data-last-notice');
                            if(typeof attr !== 'undefined' && attr !== false){
                            	last_page = true;
                            }
                    	}
                    	else{
                    		last_page = true;
                    	}
                    	if(last_page){
                    		$win.off("scroll.ajaxload");
                            $(".load-more").hide();
                            $(".loading-please-wait").hide();
                    		window.stopTimeOut();
                    	}
                    }
                });
            }
        });
    };
    
    window.loadSearchResults = function(query) {
        $(".hide-on-search").hide();
        $win.off("scroll.ajaxload");
        $(".wiki-info img").off("load error");
        $results.empty();
        $(".loading-please-wait").show();
        $.ajax({
            url: urls.ajax_search,
            data: query,
            dataType: "html",
            success: function(html) {
                $results.html(html);
                bindResultsMouseover();
                $(".loading-please-wait").hide();
                scrollLoad(query);
                resizeWikiInfo();
                $("html,body").animate({scrollTop:$(".results").offset().top}, 500);
            }
        });
    };
    
    /* Resizing text in the wikipedia abstract in search results */
    
    var currentAbstract, currentUri, currentW, currentH;
    
    function resizeWikiInfo(force) {
        var $wikinfo = $(".wiki-info");
        if (!$wikinfo.length) {
            return;
        }
        var uri = $wikinfo.attr("data-dbpedia-uri"), w = $wikinfo.width(), h = $wikinfo.height(), $wiabstract = $wikinfo.find(".wiki-info-abstract");
        if (uri === currentUri) {
            if (w === currentW && h === currentH && !force) {
                return;
            }
        } else {
            currentUri = uri;
            currentAbstract = $wiabstract.text();
        }
        currentW = w;
        currentH = h;
        var leftSpace = h - ($wikinfo.find(".wiki-info-title").outerHeight(true) + $wikinfo.find(".wiki-info-source").outerHeight(true));
        $wiabstract.text(currentAbstract);
        var shortenedAbstract = currentAbstract;
        while ($wiabstract.height() > leftSpace) {
            shortenedAbstract = shortenedAbstract.replace(/\s[\S]+$/,'…');
            $wiabstract.text(shortenedAbstract);
        }
    }
    
    resizeWikiInfo();
    
    window.onWikiImageLoad = function() {
        resizeWikiInfo(true);
    };
    window.onWikiImageError = function(img) {
        $(img).hide();
        resizeWikiInfo(true);
    };
    
    /* */
    
    $win.resize(function() {
        adaptGrid();
        recentreDbpediaBox();
        resizeWikiInfo();
    }).scroll(recentreDbpediaBox);
    
    $overlayImg.load(recentreDbpediaBox);
        
    $(".language-menu-link").click(function() {
        $(".language-menu").slideToggle();
    });
    
    $(".main-menu-link").click(function() {
        $(".main-menu").slideToggle();
    });
    
    $(".language-menu a").click(function() {
        $(".language-input").val($(this).attr("data-language-code"));
        $(".language-form").submit();
        return false;
    });
    
});
