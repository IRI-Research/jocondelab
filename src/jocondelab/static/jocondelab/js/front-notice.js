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
        
    $('.notice-images a').magnificPopup({type:'image'});
    dbpediaBox.bind(".notice-term a");
    
    var lang = document.querySelector("html").lang.substr(0,2) || "fr",
        labelsCache = {},
        dbpCache = {},
        eventCache = {},
        errorCache = {};
        
    var sparqlTpl = _.template(
        'select distinct * where { ?s rdfs:label "<%= label %>"@<%= lang %> . '
        + 'OPTIONAL { ?s dbpedia-owl:abstract ?a. FILTER(langMatches(lang(?a),"<%= lang %>")) }. '
        + 'OPTIONAL { ?s dbpedia-owl:thumbnail ?t }. '
        + 'OPTIONAL { ?s dbpedia-owl:wikiPageRedirects ?r }. ' 
        + 'OPTIONAL { ?r rdfs:label ?lr. FILTER(langMatches(lang(?lr),"<%= lang %>")) }. '
        + 'OPTIONAL { ?r dbpedia-owl:thumbnail ?tr }. '
        + 'OPTIONAL { ?s dbpedia-owl:wikiPageDisambiguates ?d }. '
        + 'OPTIONAL { ?d rdfs:label ?ld FILTER( langMatches(lang(?ld), "<%= lang %>") ) }. '
        + 'FILTER(!regex(?s, ":[^/]+$" ) && regex(?s, "^http://[^/]+/resource/")) }'
    );
            
    function getDbpedia(label, callback, errorcb) {
        
        function onBindingsLoaded(sparqlData) {
            var bindings = sparqlData.results.bindings,
                b = bindings[0],
                res = {
                    label: label,
                    wikipedia_url: "http://" + lang + ".wikipedia.org/wiki/" + encodeURIComponent(label.replace(/ /g,'_'))
                };
            
            if (b.a) { res.abstract = b.a.value; }
            if (b.ar) { res.abstract = b.ar.value; }
            if (b.t) { res.thumbnail = b.t.value; }
            if (b.tr) { res.thumbnail = b.tr.value; }
            if (b.lr) {
                res.disambiguations = [];
                res.disambiguations.push(b.lr.value);
            }
            if (b.s) { res.dbpedia_uri = b.s.value; }
            if (bindings.length > 1) {
                res.disambiguations = res.disambiguations || [];
                _(bindings).each(function(bb) {
                    if (bb.ld) {
                        res.disambiguations.push(bb.ld.value);
                    }
                });
            }
            
            dbpCache[label] = res;
            _(eventCache[label]).each(function(cb) {
                cb(res);
            });
            delete eventCache[label];
        }
        
        function onError() {
            dbpCache[label] = false;
            _(errorCache[label]).each(function(cb) {
                cb(label);
            });
            delete errorCache[label];
        }
        
        if (dbpCache[label]) {
            //console.log("Data already in cache", dbpCache[label]);
            if (typeof callback === "function") { callback(dbpCache[label]); }
            return;
        }
        if (dbpCache[label] === false) {
            if (typeof errorcb === "function") { errorcb(label); }
            return;
        }
        if (typeof eventCache[label] === "undefined") {
            eventCache[label] = [];
            errorCache[label] = [];
        }
        if (typeof callback === "function") { eventCache[label].push(callback); }
        if (typeof errorcb === "function") { errorCache[label].push(callback); }
                
        if (typeof dbpCache[label] === "undefined") {
            dbpCache[label] = null;
            $.ajax({
                url: urls.wikipedia.fr.dbpedia_sparql_url,
                data: {
                    query: sparqlTpl( { label: label, lang: lang } ),
                    format: "application/sparql-results+json"
                },
                dataType: "json",
                success: function(data) {
                    if (data.results.bindings.length) {
                        //console.log("Data found in french DbPedia", data.results.bindings[0]);
                        onBindingsLoaded(data);
                    } else {
                        if (lang !== "fr" && urls.wikipedia[lang]) {
                            $.ajax({
                                url: urls.wikipedia[lang].dbpedia_sparql_url,
                                data: {
                                    query: sparqlTpl({ label: label, lang: lang }),
                                    format: "application/sparql-results+json"
                                },
                                dataType: "json",
                                success: function(data) {
                                    if (data.results.bindings.length) {
                                        //console.log("Data found in", lang, "DbPedia", data.results.bindings[0]);
                                        onBindingsLoaded(data);
                                    } else {
                                        //console.log("Data not found in", lang, "DbPedia");
                                        onError();
                                    }
                                },
                                error: onError
                            });
                        } else {
                            //console.log("Data not found in french DbPedia and there is no known endpoint for ", lang);
                            onError();
                        }
                    }
                },
                error: onError
            });
        }
    }
    
    var $curitem = null,
        $overlay = $(".dbpedia-overlay"),
        $overlayImg = $overlay.find("img"),
        $h2 = $overlay.find("h2"),
        $abstract = $overlay.find(".dbpedia-abstract"),
        $source = $overlay.find(".dbpedia-source a"),
        hovering = false;
    
    $overlay.hover(function() {
        hovering = true;
    }, function() {
        hovering = false;
        hideOverlay();
    });
    
    function hideOverlay() {
        if (!$curitem && !hovering) {
            $overlayImg.attr("src","");
            $overlay.hide();
        }
    }
    
    function showOverlay(termdata) {
        if (!$curitem) {
            return;
        }
        var o = $curitem.offset();
        $overlay.css({
            top: o.top + $curitem.outerHeight(),
            left: o.left + $curitem.outerWidth(true) / 2,
        }).show().attr("data-dbpedia-uri", termdata.dbpedia_uri);
        if (termdata.thumbnail) {
            $overlayImg.attr("src",termdata.thumbnail).show();
        } else {
            $overlayImg.hide();
        }
        $h2.text(termdata.label);
        $abstract.text((termdata.abstract || "").replace(/^(.{240,260})\s.+$/,'$1…').substr(0,261));
        if (termdata.disambiguations) {
            var ul = $('<ul>');
            _(termdata.disambiguations).forEach(function(d) {
                ul.append(
                    $('<li>').append(
                        $('<a href="#">').click(function() {
                            $(".notice-contribution-field").val(d);
                            return false;
                        }).text(" → " + d)
                    )
                );
            });
            $abstract.append(ul);
        }
        $source.attr("href", termdata.wikipedia_url);
    }
    
    var tmpTemplate = '<li class="notice-term term-translated"></li>',
        $ntl = $(".notice-contribution-list"),
        $ncf = $(".notice-contribution-field");
    
    $(".contribution-frame").submit(function() {
        var val = $ncf.val(),
            dbpedia_uri = dbpCache[val] ? dbpCache[val].dbpedia_uri : undefined,
            $tmpItem = $(tmpTemplate).text(gettext("Validation en cours…"));
        $ncf.val("");
        $ntl.append($tmpItem);
        $.ajax({
            url: urls.ajax_contribute,
            dataType: "html",
            type: "POST",
            data: {
                csrfmiddlewaretoken: csrf_token,
                notice_id: notice_id,
                label: val,
                thesaurus_label: $ncf.attr("data-thesaurus-label")
            },
            success: function(html) {
                var $el = $(html),
                    samecontrib = $ntl.find("[data-contribution-id='" + $el.attr("data-contribution-id") + "']");
                if (samecontrib.length) {
                    samecontrib.replaceWith($el);
                } else {
                    $ntl.append($el);
                }
                $tmpItem.remove();
                dbpediaBox.bind($el.find("a"));
            },
            error: function() {
                $tmpItem.remove();
                alert(gettext("Validation impossible"));
            }
        });
        return false;
    });
    $.widget( "custom.halfwidthautocomplete", $.ui.autocomplete, {
        _resizeMenu: function() {
            this.menu.element.outerWidth(this.element.outerWidth()/2);
        }
    });
    $ncf.halfwidthautocomplete({
        source: function( request, response ) {
            if (labelsCache[request.term]) {
                response(labelsCache[request.term]);
            }
            if (typeof labelsCache[request.term] === "undefined") {
                labelsCache[request.term] = false;
                $.ajax({
                   url : "http://" + lang + ".wikipedia.org/w/api.php",
                   dataType: "jsonp",
                   data : {
                       action: "opensearch",
                       search: request.term,
                       format: "json",
                       limit: 10
                   },
                   success: function( data ) {
                       labelsCache[request.term] = _.map( data[1], function(item) {
                           return {
                               label: item,
                               value: item
                           };
                       });
                       response(labelsCache[request.term]);
                   }
                });
            }
        },
        focus: function(e, ui) {
            $curitem = $(this);
            hovering = false;
            $overlay.hide();
            getDbpedia(ui.item.label, showOverlay);
        },
        select: function(e, ui) {
            $ncf.val(ui.item.label);
            $(".contribution-frame").submit();
            return false;
        },
        close: function(e, ui) {
            $curitem = null;
            hideOverlay();
        },
        minLength: 2
    });
    
    $(".notice-contribution-list").on("click",".contribution-upvote, .contribution-downvote, .contribution-remove", function() {
        var $this = $(this),
            $li = $(this).parents("li"),
            $list = $li.parent(),
            endpoint = urls[$this.hasClass("contribution-upvote") ? "upvote" : "downvote"];
        $.ajax({
            url: endpoint,
            dataType: "html",
            type: "POST",
            data: {
                csrfmiddlewaretoken: csrf_token,
                contribution_id: $li.attr("data-contribution-id"),
            },
            success: function(html) {
                if ($list.hasClass("contribution-novote")) {
                    $li.hide();
                } else {
                    $li.replaceWith($(html));
                }
                
            }
        });
        return false;
    });
        
});
