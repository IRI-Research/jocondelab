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

$(function() {
    
    var startYear = -20000,
        endYear = 2012,
        gamma = 2,
        zoomLevel = 4,
        minZoomLevel = 0,
        maxZoomLevel = 14,
        sliderWidth = 3000,
        $slider = $(".timeline-mill-slider"),
        $zoomSlider = $(".timeline-slider"),
        $tlcontainer = $(".timeline-container"),
        canvas = $tlcontainer.find('canvas')[0],
        lineDistances = [ 50000, 25000, 10000, 5000, 2500, 1000, 500, 250, 100, 50, 25, 10, 5, 2 ],
        miniLines = [-20000, -5000, -2000, -1000, 0, 1000, 2000],
        wCenter = .875,
        itemCount = 12,
        tlCache = [], tlIdCache = [], currentTerm = null,
        startSlide = startYear, endSlide = endYear, userStartSlide = startSlide, userEndSlide = endSlide,
        fromYear, toYear, cWidth, wLineDist, zoomFactor,
        isRtl = $("html").is("[dir=rtl]");
    
    /*
     *  HOW UNIT CONVERSIONS WORK ?
     * 
     *  First, Years from startYear (-20K) to endYear (now) are mapped to a [0,1] range that we call T
     *    - tToYr converts units in this range to years, and yrToT does the reverse conversion
     *  
     *  Then, a non-linear scale is applied to have a focus on recent years.
     *  In this case, I chose a gamma correction : y = x^gamma which also yields a [0,1] range
     *    - The Years-Based ranged is converted to the range used for pixel distances with the function
     *      wToT (reverse tToW -> x = y^(1/gamma))
     *  
     *  This new range "w" is used for all pixel distance calculations.
     *  
     *  For the "mini-Timeline" (full year range, at the top), these are converted directly
     * 
     *  For the main timeline, which only show a subset (window) of the full timeline,
     *  two more parameters are required :
     *    - The zoom level (variable zoomLevel)
     *    - The position of the centre of the window relative to the range (called wCenter)
     *  
     *  The year range of our window is calculated from these parameters
     *  
     *  Each time we zoom in, the scale is increased by 41 % (that's the square root of 2
     *  and also the ratio between An and An-1 - e.g. A4 and A3 paper sheets)
     *  This way, the scale is proportional to 1.41 to the power of the zoom level.
     *  This is why we calculate a zoomFactor from zoomLevel
     *  
     * 
     * */
    
    function tToW(t) {
        //return 2 / (2-Math.min(1,Math.max(0,t))) - 1,;
        return Math.pow(t, gamma);
    }
    function wToT(w) {
        //return 2 - 2/(Math.min(1,Math.max(0,w))+1);
        return Math.pow(w, 1/gamma);
    }
    function tToYr(t) {
        return startYear + (endYear - startYear) * t;
    }
    function yrToT(yr) {
        return (yr - startYear)/(endYear - startYear);
    }
    function wToYr(w) {
         return tToYr(wToT(w));
    }
    function yrToW(yr) {
        return tToW(yrToT(yr));
    }
    function deltaXToDeltaW(dx) {
        return (isRtl ? -1 : 1) * dx / (zoomFactor * cWidth);
    }
    function deltaWToDeltaX(dw) {
        return (isRtl ? -1 : 1) * dw * zoomFactor * cWidth;
    }
    function wToX(w) {
        return (isRtl ? cWidth : 0) + deltaWToDeltaX(w - wCenter + (.5 / zoomFactor));
    }
    function xToW(x) {
        return deltaXToDeltaW(x - (isRtl ? cWidth : 0)) + wCenter - (.5 / zoomFactor);
    }
    function wToMini(w) {
        var res = cWidth * w;
        if (isRtl) {
            res = cWidth - res;
        }
        return res;
    }
    function deltaMiniToDeltaW(m) {
        return (isRtl ? -1 : 1) * m / cWidth;
    }
    function miniToW(m) {
        var res = deltaMiniToDeltaW(m);
        if (isRtl) {
            res = cWidth - res;
        }
        return res;
    }
    function wToSlider(w) {
        var res = zoomFactor * sliderWidth * (w - wCenter + (.5 / zoomFactor));
        if (isRtl) {
            res = sliderWidth - res;
        }
        return res;
    }
    function sliderToW(slidepos) {
        var p = slidepos;
        if (isRtl) {
            p = sliderWidth - p;
        }
        return p / (sliderWidth * zoomFactor) + wCenter - (.5 / zoomFactor);
    }
    function yrToMiniX(yr) {
        return wToMini(yrToW(yr));
    }
    function yrToX(yr) {
        return wToX(yrToW(yr));
    }
    function yrToSliderPos(yr) {
        return wToSlider(yrToW(yr));
    }
    function sliderPosToYr(slidepos) {
        return wToYr(sliderToW(slidepos));
    }
    function boundValue(val) {
        return Math.max(Math.floor(fromYear), Math.min(Math.floor(toYear), val));
    }
    function updateZoomFactor() {
        zoomFactor = Math.pow(2, zoomLevel/2);
    }
    function updateSlider() {
        startSlide = boundValue(userStartSlide);
        endSlide = boundValue(userEndSlide);
        var startPos = yrToSliderPos(startSlide),
            endPos = yrToSliderPos(endSlide);
        $slider.slider("values",[Math.min(startPos, endPos),Math.max(startPos, endPos)]);
        updateSpans();
    }
    function updateCoords() {
        /* Let's first check if the timeline width has been changed */
        cWidth = $tlcontainer.width();
        cHeight = $tlcontainer.height();
        wLineDist = null;
        /* We calculate the bounding years of our window */
        fromYear = wToYr(wCenter - .5 / zoomFactor);
        toYear = wToYr(wCenter + .5 / zoomFactor);
        /*
         We want to choose the distance between lines that we want to display, so that
         two lines at the first quarter of our range are more than 50 pixels apart.
        */
        var wAtQuarter = (wCenter - .25 /zoomFactor),
            yearAtQuarter = wToYr(wAtQuarter),
            posAtQuarter = wToX(wAtQuarter);
        for (var i = 0; i < lineDistances.length; i++) {
            var yr = yearAtQuarter + lineDistances[i],
                x = yrToX(yr),
                delta = x - posAtQuarter;
            if (Math.abs(delta) < 50) {
                break;
            }
            wLineDist = lineDistances[i];
        }
        /* If the slider range is larger than the window, we constrain it to the window */
        updateSlider();
    }
    
    var itemTpl = _.template(
        '<li class="timeline-item"><div class="timeline-item-box<%- current ? " timeline-current" : "" %>"'
        + ' data-dbpedia-uri="<%- dbpedia_uri %>" style="left: <%- left %>px; width: <%- width %>px;">'
        + '<div class="timeline-item-label"><%- label %></div></div></li>'
    );
    
    function redrawView() {
        canvas.width = cWidth;
        canvas.height = cHeight;
        var ctx = canvas.getContext("2d"),
            xstart = yrToMiniX(fromYear),
            xend = yrToMiniX(toYear),
            xleft = Math.min(xstart, xend),
            xright = Math.max(xstart, xend);
        
        /* We first draw the darkish rectangle showing the full timeline */
        ctx.fillStyle = "#e0e0e0";
        ctx.fillRect( 0, 0, cWidth, cHeight/14 );
        /* We draw the rectangle for the main timeline */
        ctx.fillStyle = "#f8f8f8";
        ctx.fillRect(0, cHeight/7, cWidth, cHeight*6/7);
        /* We now draw the blue "funnel" showing the relationship between timelines */
        ctx.fillStyle = "rgba(0, 64, 255, .05)";
        ctx.strokeStyle = "#3090ff";
        ctx.beginPath();
        ctx.moveTo(xleft, 0);
        ctx.lineTo(xright, 0);
        ctx.lineTo(xright, cHeight/14);
        ctx.lineTo(cWidth, cHeight/7);
        ctx.lineTo(cWidth, cHeight);
        ctx.lineTo(0, cHeight);
        ctx.lineTo(0, cHeight/7);
        ctx.lineTo(xleft, cHeight/14);
        ctx.closePath();
        ctx.stroke();
        ctx.fill();
        /* Whoaw, that was a long line to draw */
        /* Now, we draw the years on the full timeline */
        ctx.font = 'bold 12px Arial,Helvetica';
        ctx.fillStyle = "#333333";
        ctx.strokeStyle = "#333333";
        for (var i = 0; i < miniLines.length; i++ ) {
            var y = miniLines[i],
                x = yrToMiniX(y);
            ctx.beginPath();
            ctx.moveTo(x,0);
            ctx.lineTo(x,cHeight/70);
            ctx.moveTo(x,cHeight*2/35);
            ctx.lineTo(x,cHeight/14);
            ctx.stroke();
            ctx.textAlign = (i ? (i == miniLines.length - 1 ? (isRtl ? "left" : "right" ) : "center") : (isRtl ? "right" : "left" ) );
            ctx.fillText(y || 1, x,cHeight/21);
        }
        /* Now, we draw the years on the main timeline */
        ctx.textAlign = 'center';
        ctx.font = 'bold 14px Arial,Helvetica';
        ctx.fillStyle = "#000000";
        var lastX = -40;
        for (var y = wLineDist * Math.ceil(fromYear/wLineDist); y <= toYear; y += wLineDist ) {
            var x = yrToX(y),
                isPrimary = !((y/wLineDist) % 2);
            ctx.strokeStyle = (isPrimary ? "#000000": "#999999");
            ctx.beginPath();
            ctx.moveTo(x, cHeight*3/14);
            ctx.lineTo(x, cHeight - cHeight/14);
            ctx.stroke();
            // 40 is a bit arbitrary but avoids overlap
            if (isPrimary && (y!=startYear) && (x>(lastX+40))) {
                ctx.fillText(y || 1, x, cHeight - 4);
                ctx.fillText(y || 1, x, cHeight*4/21);
                lastX = x;
            }
        }
        /* Now displaying the different terms that we will show on the timeline */
        var html = _(tlCache).chain()
            .filter(function(item) { // Only show those within the range
                return (item.end_year > fromYear && item.start_year < toYear && item.label);
            }).first(itemCount) // Take the first 12
            .sortBy(function(item) { // Sort by mean year
                return (item.start_year + item.end_year);
            }).map(function(item) { // Render them as HTML
                var l = Math.min(cWidth, Math.max(0, yrToX(Math.max(item.start_year, fromYear)))),
                    r = Math.min(cWidth, Math.max(0, yrToX(Math.min(item.end_year, toYear) + 1)));
                return itemTpl({
                    current: (item.dbpedia_uri == currentTerm),
                    dbpedia_uri: item.dbpedia_uri,
                    label: (item.label.length > 24) ? item.label.substr(0,20) + '…' : item.label,
                    left: Math.min(l,r),
                    width: Math.abs(r-l)
                });
            }).value().join("");
        $(".timeline-list").html(html);
        // Binding events to the freshly rendered HTML
        dbpediaBox.bind(".timeline-item-box");
        $(".timeline-item-box").click(function() {
            var $this = $(this);
            currentTerm = $this.attr("data-dbpedia-uri");
            $(".timeline-item-box").removeClass("timeline-current");
            $this.addClass("timeline-current");
            loadSearchWithState({ dbpedia_uri: currentTerm });
        });
        $(".timeline-span-from").text(Math.round(fromYear) || 1);
        $(".timeline-span-to").text(Math.round(toYear));
    }
    
    function setCenter(c) {
        var halfSpan = .5/zoomFactor;
        wCenter = Math.max(halfSpan, Math.min(1 - halfSpan, c));
        throttledRedraw();
        debouncedGetData();
    }
    
    function setZoomLevel(level, center) {
        var c = (typeof center === "number" ? center : wCenter);
        zoomLevel = Math.max(minZoomLevel, Math.min(maxZoomLevel, level));
        $zoomSlider.slider("value",zoomLevel);
        updateZoomFactor();
        setCenter(c);
    }
  
    function getData() {
        $.getJSON(
            urls.ajax_years,
            {
                from_year: Math.floor(fromYear),
                to_year: Math.floor(toYear)
            },
            function(data) {
                _(data).each(function(term) {
                    if (tlIdCache.indexOf(term.dbpedia_uri) === -1) {
                        tlIdCache.push(term.dbpedia_uri);
                        tlCache.push(term);
                    }
                });
                tlCache = _(tlCache).sortBy(function(item) {
                    return -item.nb_notice;
                });
                throttledRedraw();
            }
        );
    }
    
    function loadSearchWithState(data) {
        window.history.pushState(data, "", "#" + $.param(data));
        loadSearchResults(data);
    }
    function loadFromState(data) {
        loadSearchResults(data);
        if (data.dbpedia_uri) {
            $(".timeline-item-box").removeClass("timeline-current");
            $(".timeline-item-box[data-dbpedia-uri='" + data.dbpedia_uri + "']").addClass("timeline-current");
        }
        if (typeof data.from_year !== "undefined" && typeof data.to_year !== "undefined") {
            userStartSlide = parseInt(data.from_year);
            userEndSlide = parseInt(data.to_year);
            updateSlider();
        }
    }

    var throttledRedraw = _.throttle(function() {
        updateCoords();
        redrawView();
    }, 100);
    
    var debouncedGetData = _.debounce(getData, 1000);
        
    var wcStart, dragmini, startLevel,
        h = Hammer($tlcontainer[0]);
    
    h.on("dragstart", function(e) {
        if (!e.gesture) {
            return;
        }
        dragmini = (e.gesture.center.pageY - $tlcontainer.offset().top < 40);
        wcStart = wCenter;
    }).on("drag", function(e) {
        if (!e.gesture) {
            return;
        }
        setCenter(
            dragmini ?
            (wcStart + deltaMiniToDeltaW(e.gesture.deltaX)) :
            (wcStart - deltaXToDeltaW(e.gesture.deltaX))
        );
        e.gesture.preventDefault();
    }).on("tap", function(e) {
        var o = $tlcontainer.offset();
        if (e.gesture && e.gesture.center.pageY - o.top < 40) {
            setCenter(miniToW(e.gesture.center.pageX - o.left));
        }
    }).on("touch", function(e) {
        startLevel = zoomLevel;
    }).on("pinchin pinchout", function(e) {
        if (!e.gesture) {
            return;
        }
        var newLevel = Math.max(
            minZoomLevel,
            Math.min(
                maxZoomLevel,
                startLevel + Math.round(Math.log(e.gesture.scale)*2*Math.LOG2E)
            )
        );
        var scaleRatio = Math.pow(2, (newLevel - zoomLevel) / 2),
            wTap = xToW(e.gesture.center.pageX - $tlcontainer.offset().left);
        setZoomLevel(newLevel, wTap * (1 - 1 / scaleRatio) + wCenter / scaleRatio);
        e.gesture.preventDefault();
    });
    
    var arrowTo, arrowDir = false;
    
    function goGoGo() {
        if (arrowDir) {
            setCenter(wCenter + arrowDir/(100*zoomFactor));
        }
    }
    
    setInterval(goGoGo, 100);
    
    $(".timeline-arrows a").on("mousedown touchstart", function() {
        arrowDir = parseInt($(this).attr("data-direction"));
        return false;
    }).on("mouseout touchend", function() {
        arrowDir = false;
    });
    $("body").mouseup(function() {
        arrowDir = false;
    });
    
    $tlcontainer.mousewheel(function(e, d) {
        var wMouse = xToW(e.pageX - $tlcontainer.offset().left),
            zoomDelta = (d > 0 ? 1 : -1),
            scaleRatio = Math.pow(2, zoomDelta/2);
        if (d < 0 && zoomLevel <= minZoomLevel) {
            return;
        }
        if (d >= 0 && zoomLevel >= maxZoomLevel) {
            return;
        }
        setZoomLevel(zoomLevel + zoomDelta, wMouse * (1 - 1 / scaleRatio) + wCenter / scaleRatio);
        return false;
    });
    
    var $startSpan = $(".timeline-mill-from-year"),
        $endSpan = $(".timeline-mill-to-year");
    
    function updateSpans() {
        $startSpan.text(startSlide);
        $endSpan.text(endSlide);
    }
    
    updateSpans();
    
    $slider.slider({
        range: true,
        min: 0,
        max: sliderWidth,
        values: [0, sliderWidth],
        slide: function(e, ui) {
            var y0 = Math.floor(sliderPosToYr(ui.values[0])),
                y1 = Math.floor(sliderPosToYr(ui.values[1]));
            userStartSlide = startSlide = Math.min(y0,y1);
            userEndSlide = endSlide = Math.max(y0,y1);
            updateSpans();
        }
    });
    
    $zoomSlider.slider({
        orientation: "vertical",
        min: minZoomLevel,
        max: maxZoomLevel,
        range: "min",
        value: zoomLevel,
        slide: function(e, ui) {
            setZoomLevel(ui.value);
        }
    });
    
    $(".timeline-zoom-in").click(function() {
        setZoomLevel(zoomLevel + 1);
    });
    
    $(".timeline-zoom-out").click(function() {
        setZoomLevel(zoomLevel - 1);
    });
    
    $(".timeline-mill-submit").click(function() {
        loadSearchWithState({ from_year: startSlide, to_year: endSlide, show_years: 1 });
    });
    
    updateZoomFactor();
    throttledRedraw();
    getData();
    
    $(window).resize(throttledRedraw);
        
    var hash = document.location.hash.replace(/^#/,'')
    if (hash) {
        var paramtables = hash.split('&'),
            firstState = {};
        _(paramtables).each(function(p) {
            var t = p.split('=');
            firstState[t[0]] = t[1];
        });
        loadFromState(firstState);
    } else {
        var firstState = null;
    }
    
    $(window).on("popstate", function(e) {
        var state = e.originalEvent.state || firstState;
        if (state) {
            loadFromState(state);
        } else {
            $(".timeline-item-box").removeClass("timeline-current");
            $(".results").empty();
            var $body = $("html,body"),
                headoff = $("header").offset().top;
            if ($body.scrollTop() > headoff) {
                $("html,body").animate({scrollTop:headoff}, 500);
            }
        }
    });
    
});
