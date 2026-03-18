var _____WB$wombat$assign$function_____=function(name){return (self._wb_wombat && self._wb_wombat.local_init && self._wb_wombat.local_init(name))||self[name];};if(!self.__WB_pmw){self.__WB_pmw=function(obj){this.__WB_source=obj;return this;}}{
let window = _____WB$wombat$assign$function_____("window");
let self = _____WB$wombat$assign$function_____("self");
let document = _____WB$wombat$assign$function_____("document");
let location = _____WB$wombat$assign$function_____("location");
let top = _____WB$wombat$assign$function_____("top");
let parent = _____WB$wombat$assign$function_____("parent");
let frames = _____WB$wombat$assign$function_____("frames");
let opens = _____WB$wombat$assign$function_____("opens");
/*
* Bravenet jQuery Adapter
*
* Copyright (c) 2008 Bravenet Web Services Inc. (bravenet.com)
*/
(function( jQuery ) {

  if ( jQuery ) {

    // store reference to old ajax function
    var ajax_without_flash = jQuery.ajax,
    // used to make urls unique
    jsc = (new Date).getTime();

    function isRemoteUrl( s ) {
      return !!s.url.match(window.location.hostname);
    }

    function isRemoteDataType( s ) {
      return s.dataType == "script" || s.dataType == "json" || s.dataType == "jsonp";
    }

    function isGetRequest( s ) {
      return s.type.toLowerCase() == "get";
    }

    // extend ajax with our xd flash technique
    jQuery.extend({
      ajax: function( s ) {
        s = jQuery.extend( true, s, jQuery.extend( true, {}, jQuery.ajaxSettings, s ) );

        // convert data if not already a string
        if ( s.data && s.processData && typeof s.data != "string" )
        s.data = jQuery.param(s.data);

        if ( isGetRequest( s ) && isRemoteDataType( s ) ) {
          return ajax_without_flash( s );
        }

        var uid = jsc++;
        var o = Bravenet[ '_xd_' + uid ] = {
          callbacks: {},
          originals: {}
        };
        jQuery.each( [ 'complete', 'success', 'error' ], function(index, value) {
          if ( typeof(s[ value ]) != 'function' ) { return true; }

          o.callbacks[ value ] = function( text ) {
            unescaped = unescape( text );
            var resp = {
              responseText: unescaped,
              responseXml: unescaped
            };
            o.originals[ value ](resp, 'success');
            delete Bravenet[ '_xd_' + uid ];
          };

          o.originals[ value ] = s[ value ];
          s[ value ] = "Bravenet[ '_xd_"+uid+"' ].callbacks[ '"+value+"' ]";
        });

        Bravenet._xd_ajax.ajax( s );
      }
    });

    var original_serializeArray = jQuery.fn.serializeArray;
    jQuery.fn.extend({
      serializeArray: function(encode) {
        var serialized = original_serializeArray.apply(this);
        if (encode) {
          serialized = serialized.map(function(dict) {
            return { name: dict.name, value: Bravenet.encode(dict.value) };
          });
        }
        return serialized;
      }
    });

    // remap jQuery into the Bravenet namespace
    window.Bravenet.jQuery = jQuery.noConflict(true);
  }

  if (Bravenet.Core) {
    // now launch the service
    Bravenet.Core.launch();
  }
})( window.jQuery );

}

/*
     FILE ARCHIVED ON 12:52:16 Jun 19, 2011 AND RETRIEVED FROM THE
     INTERNET ARCHIVE ON 20:16:07 Mar 17, 2026.
     JAVASCRIPT APPENDED BY WAYBACK MACHINE, COPYRIGHT INTERNET ARCHIVE.

     ALL OTHER CONTENT MAY ALSO BE PROTECTED BY COPYRIGHT (17 U.S.C.
     SECTION 108(a)(3)).
*/
/*
playback timings (ms):
  capture_cache.get: 16.75
  load_resource: 72.574
  PetaboxLoader3.resolve: 27.905
  PetaboxLoader3.datanode: 30.214
*/