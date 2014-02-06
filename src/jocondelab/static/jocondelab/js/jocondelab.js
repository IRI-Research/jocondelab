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

﻿// -*- coding: utf-8 -*-
function fill_wp_infobox(item) {

    var wp_infobox = $("#wp-infobox");
    if(wp_infobox.length === 0) {
        wp_infobox = $("<div>",{id: 'wp-infobox'}).addClass( "ui-widget-content ui-corner-all").appendTo('body');
    }
    
    wp_infobox.find('img').off('error');
    
    
    
    var html_str = "<h3>"+item.label+"</h3>" +
    (item.original_label !== item.label ? "<h4>" + gettext("Redirected from: ") + item.original_label+"</h4>":"") +
    "<div class='wp-infobox-wp-link'>" +
    "<a target='_blank' href='"+ item.url +"'>" + gettext("Source wikipedia") + "</a>" +
    "</div>" +
    (item.thumbnail?"<img class='wp-img' src=\""+ item.thumbnail+"\"/>":"") +
    "<div>" + item.abstract + "</div>" ;    
    
    wp_infobox.html(html_str);
    
    wp_infobox.find('img').error(function(){
        $(this).attr('src',static_url+"jocondelab/img/Wikipedia-logo-v2-fr.png");
        $(this).off('error');
    });
    
    wp_infobox
        .position({my: "left top", at:"right+5 top", of: $(".ui-autocomplete")})
        .css("z-index", $(".ui-autocomplete").css("z-index"))
        .show();
}

function get_dp_sparql(resource_url, wp_lang) {
    return "select distinct ?s ?t ?y ?l ?r where { " +
    "<"+resource_url+"> rdfs:label ?s . FILTER(langMatches(lang(?s), \""+wp_lang+"\")) . " +
    "OPTIONAL { <"+resource_url+"> dbpedia-owl:thumbnail ?t } . " +
    "OPTIONAL { <"+resource_url+"> dbpedia-owl:abstract ?y . FILTER(langMatches(lang(?y), \""+wp_lang+"\")) } . "+
    "OPTIONAL { <"+resource_url+"> foaf:isPrimaryTopicOf ?l } " +
    "OPTIONAL { <"+resource_url+"> dbpedia-owl:wikiPageRedirects ?r } " +
    "} LIMIT 100"
}

function get_dp_ajax(resource_url, wp_lang) {
    var url;
    if(wikipedia_urls[wp_lang]['dbpedia_sparql_use_proxy']) {
        url = wp_sparql_proxy_url.replace(/XY(\/?)$/,wp_lang+"$1"); 
    }
    else {
        url = wikipedia_urls[wp_lang]['dbpedia_sparql_url'];
    }
    return $.ajax({
        url: url,
        data: {
            query: get_dp_sparql(resource_url, wp_lang),
            format: "application/sparql-results+json"
        },
        dataType: "json",
        cache: true
    })
}

function init_term_events()
{
    // Tag simple operations : activate/unactivate wp link, remove wp link
    $(".remove_wp_link").click(function(e){
        msg = interpolate(gettext("Confirmez-vous la suppression du lien Wikipédia pour le terme \"%s\" ?"),[$(this).attr('alt')]);
        if(confirm(msg)){
            delete_link(this);
        }
    });
    
    $(".wikipedia_edition").click(function(e) {
        $.post(term_wikipedia_edition_url,
            {
                csrfmiddlewaretoken:global_csrf_token, 
                term_id:term_id,
                wikipedia_edition: $(this).is(':checked')
            },
            function(data, textStatus) {
                window.location.reload(true);
            }
        );
    });
    
    $("#wp_link_semantic_level").change(function(e) {
        $.post(link_semantic_level_url,
            {
                csrfmiddlewaretoken:global_csrf_token, 
                term_id:term_id,
                link_semantic_level: $("#wp_link_semantic_level").val()
            },
            function(data, textStatus) {
                window.location.reload(true);
            }
        );
    });
    
    // Wikipedia search management (new tag)
    $("#wp_search").autocomplete({
        source: function( request, response ) {
            var wp_lang = $('#wp_lang').val()
            $.ajax({
               url : wikipedia_urls[wp_lang]['api_url'],
               dataType: "jsonp",
               data : {
                   action: "opensearch",
                   search: request.term,
                   format: "json",
                   limit: 10                   
               },
               success: function( data ) {
                   response( $.map( data[1], function( item ) {
                       return {
                           label: item,
                           value: item
                       };
                   }));
               }
            });
        },
        select: function(event, ui) { 
            // Since the event still did not update wp_search's val, we force it.
            $("#wp_search").val(ui.item.label);
            select_done = true;
            $("#ok_search").click();
        },
        minLength: 2,
        open: function() {
            $( this ).removeClass( "ui-corner-all" ).addClass( "ui-corner-top" );
        },
        close: function() {
            $( this ).removeClass( "ui-corner-top" ).addClass( "ui-corner-all" );
            setTimeout(function(){$("#wp-infobox").hide();},500);
            var request = $("#wp_search").data('request');
            var chained = $("#wp_search").data('chained');
            if(request) {
                request.abort();
            }
            if(chained && typeof(chained.abort) === typeof(Function)) {
                chained.abort();
            }
        },
        focus: _.debounce(function(event,ui) {
            
            var page_name = ui.item.label.replace(/ /g, "_");
            var wp_lang_code = $('#wp_lang').val();
            var resource_url = wikipedia_urls[wp_lang_code]['dbpedia_uri'].replace(/\%s/,page_name);
            var wp_page_url = wikipedia_urls[wp_lang_code]['page_url'] + "/" + page_name;
            var request = $("#wp_search").data('request');
            var chained = $("#wp_search").data('chained');
            if(request) {
                request.abort();
            }
            if(chained && typeof(chained.abort) === typeof(Function)) {
                chained.abort();
            }
            request = get_dp_ajax(resource_url, wp_lang_code);
            $("#wp_search").data('request',request);
            chained = request.then(function(data) {
                $("#wp_search").data('request', null);
                res = data.results.bindings.length>0?data.results.bindings[0]:{y:"",l:wp_page_url,t:"", r:""};                        
                if(res.r) {
                    return get_dp_ajax(res.r.value, wp_lang_code);
                }
                else {
                    return data;
                }
            });
            $("#wp_search").data('chained',chained);
            chained.done(function(data) {
                $("#wp_search").data('chained', null);
                res = data.results.bindings.length>0?data.results.bindings[0]:{s:ui.item.label, y:"",l:wp_page_url,t:"", r:""};                
                var item = {
                    label : res.s?res.s.value:ui.item.label,
                    original_label : ui.item.label,
                    abstract: res.y?res.y.value:"",
                    url: res.l?res.l.value:"",
                    thumbnail: res.t?res.t.value:""
                };                
                fill_wp_infobox(item);
            });
        }, 500)
    })
    .data( "ui-autocomplete" )._renderItem = function( ul, item ) {
        label = item.titlesnippet;
        if(!label) {
            label = item.label;
        }
        return $( "<li></li>" )
        .data( "item.autocomplete", item )
        .append( "<a>" + label + "</a>" )
        .appendTo( ul );
    };
    $('#wp_search').keyup(function(e){
        if((e.keyCode==13) && ($("#wp_search").val()!="") && (select_done==false)){
            update_link($("#wp_search").val(), $("#wp_lang").val());
        }
        select_done = false;
    });
    $("#ok_search").click(function(){
        if($("#wp_search").val()!=""){
            update_link($("#wp_search").val(), $("#wp_lang").val());
        }
    });
    // Validate sheet management : the radiobutton name has is "'gr_validated' + datasheet.hda_id"
    $("input[type='radio'][name='gr_validated']").click(function(e){
        e.preventDefault();
        val = $("input[type='radio'][name='gr_validated']:checked").val();
        if(val === 'True') {
            msg = gettext("Confirmez-vous la validation de ce terme ?");            
        }
        else {
            msg = gettext("Confirmez-vous l'invalidation de cette fiche ?");
        }
        if(confirm(msg)) {
            $.post(validate_term_url,{term_id: term_id, validation_val: val, csrfmiddlewaretoken: global_csrf_token},function(data) {
                window.location.reload(true);
            });
        }
    });    
}


function delete_link(btn)
{
    if ($(btn).is(".remove_wp_link")) {
        var url = remove_wp_link_url;
        var term_id = $(btn).attr('id');
    }

    $.ajax({
        url: url,
        type: 'POST',
        data: {csrfmiddlewaretoken:global_csrf_token, 
               term_id:term_id,
               },
        // bug with jquery >= 1.5, "json" adds a callback so we don't specify dataType
        //dataType: 'json',
        success: function(msg, textStatus, XMLHttpRequest) {
            window.location.reload(true);
        },
		error: function(jqXHR, textStatus, errorThrown) {
			resp = $.parseJSON(jqXHR.responseText);
			console.log(resp.message);
			$(btn).html(id_tag);
		}
    });
}

function update_link(tag_label, wp_lang)
{
    $("#ok_search").html("<img src='"+static_url+"jocondelab/img/indicator.gif'>");
    var url = modify_wp_link_url;
    $.ajax({
        url: url,
        type: 'POST',
        data: {csrfmiddlewaretoken:global_csrf_token,
               term_id:term_id,
               label:tag_label,
               wp_lang:wp_lang
               },
        // bug with jquery >= 1.5, "json" adds a callback so we don't specify dataType
        //dataType: 'json',
        success: function(msg, textStatus, XMLHttpRequest) {
            window.location.reload(true);
        },
        error: function(jqXHR, textStatus, errorThrown) {
            $("#wp_search").val("");
            $("#wp_lang").val(wp_lang);
			$("#ok_search").html("<em style='color: red'>"+gettext("error when treating request")+"</em>").delay(5000).hide(400,function() {$(this).html("<b>OK</b>").show();});
        },
    });
}

function set_dialog_link_state(enabled) {
    if(enabled) {
        $( "#dialog-link-container" ).removeClass("ui-state-disabled");
        $( "#dialog-link" ).css('cursor', 'pointer');
        $( "#dialog-deselect" ).css('cursor', 'pointer');
    }
    else {
        $( "#dialog-link-container" ).addClass("ui-state-disabled");
        $( "#dialog-link" ).css('cursor', 'default');
        $( "#dialog-deselect" ).css('cursor', 'default');
    }

}

function init_filter() {

    $( "#dialog" ).dialog({
        autoOpen: false,
        width: 400,
        height: "auto",
        maxHeight: 800,
        resizable: false,
        position: {my: "left top", at:"left bottom+5", of:$("#dialog-link-container"), collision: 'none'},
        open: function(event, ui) {
            $('#term-tree')
                .jstree({
                    themes: {
                        theme: "apple",
                        dots: true,
                        icons: true
                    },
                    json_data: {
                        ajax: {
                            url : function(node) {
                                return term_tree_json_url.replace("0", $('#thesaurus').val())
                            },
                            data: function(node) {
                                var res = {} 
                                if(node.data) {
                                    res.initial_node = node.data('term_tree_node').id;
                                }                                
                                else if($('#thesaurus_tree').val()) {
                                    res.selected_node = $('#thesaurus_tree').val();
                                }                                
                                return res;
                            },
                            error: function() {
                                $(".jstree-loading").removeClass("jstree-loading").addClass("jstree-error").html("Error when loading tree");
                            }
                        },
                        progressive_render: true
                    },
                    ui : {
                        select_limit: 1,
                        initially_select: $('#thesaurus_tree').val()?['node-term-'+$('#thesaurus_tree').val()]:[]
                    },
                    types : {
                        types: {
                            "leaf" : {
                                'hover_node' : false,
                                'select_node': function () {return false;}
                            }
                        }
                    },
                    plugins : [ "themes", "json_data", "ui", "types"]
                });
        },
        close: function( event, ui ) {
            $.jstree._reference($('#term-tree')).destroy();
        },
        buttons: [
            {
                text:  gettext("Ok"),
                click: function() {
                    selected = $.jstree._reference($('#term-tree')).get_selected();
                    if(selected.length) {
                        selected_node = $(selected[0]);
                        $('#thesaurus_tree').data('term_tree_node',selected_node.data('term_tree_node'));
                        $('#thesaurus_tree').val(selected_node.data('term_tree_node').id).trigger('change');                        
                    }
                    
                    $( this ).dialog( "close" );                    
                }
            },
            {
                text: gettext("Cancel"),
                click: function() {
                    $(this).dialog( "close" );
                }
            }
        ]
    });

    // Link to open the dialog
    $( "#dialog-link" ).click(function( event ) {
        event.preventDefault();
        if(! $('#thesaurus_tree').is(":disabled")) {
            $( "#dialog" ).dialog( "open" );
        }
    });
    
    $('#thesaurus_tree').change(function(event) {
        if($(this).is(":disabled")) {
            set_dialog_link_state(false);
        }
        else {
            set_dialog_link_state(true);
            
            node = $('#thesaurus_tree').data('term_tree_node');

            if(node) {
                $('#dialog-link').text(node.label);
            }
            else {
                $('#dialog-link').text($('#dialog-link').attr('title'));
            }
        }
    });
    
    if(term_tree_valid_thesaurus.indexOf(parseInt($('#thesaurus').val())) >= 0) {
        $('#thesaurus_tree').attr('disabled',$('#thesaurus').val() === "").trigger('change');        
    }
    else {
        $('#thesaurus_tree').attr('disabled',true).trigger('change');
    }

    $('#thesaurus').change(function(e) {
        val = $(e.target).val();
        $('#thesaurus_tree').val('').data('term_tree_node',null).trigger('change');
        if(term_tree_valid_thesaurus.indexOf(parseInt(val)) >= 0) {
            $('#thesaurus_tree').attr('disabled',val === "").trigger('change');
        }
        else {
            $('#thesaurus_tree').attr('disabled',true).trigger('change');
        }
    });
    
    $('#dialog-deselect').click(function(e) {
        if(! $('#thesaurus_tree').is(":disabled")) {
            $( "#dialog" ).dialog( "close" );
            $('#thesaurus_tree').val('').data('term_tree_node',null).trigger('change');
        }
    });

    $('#order_by').change(function(e) {
        if($('#order_by').val() === 'lft') {
            $('#order_dir').prop('disabled', true);
        }
        else {
            $('#order_dir').prop('disabled', false);
        }
    })
    
}


function init_filter_events() {
    
    $('#term-filter-form').submit(function(){
        var values = $('#term-filter-form').serialize();
        $('#term-explorer-container').load(term_list_table_url, values, function() {
            init_edit_page();
        });
        return false;
    });
}

function init_edit_page() {
    $('#term-list-table #term-'+term_id).addClass('currenttermline');

    $('.pagination a').click(function(e) {
        e.preventDefault();
        var values = this.href.slice(window.location.href.indexOf('?') + 1) 
        $('#term-explorer-container').load(term_list_table_url, values, function() {
            init_edit_page();
        });
        return false;
    });
}

