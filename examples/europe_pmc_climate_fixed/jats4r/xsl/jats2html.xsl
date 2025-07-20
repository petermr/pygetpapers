<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:xs="http://www.w3.org/2001/XMLSchema"
  xmlns:html="http://www.w3.org/1999/xhtml"
  xmlns:mml="http://www.w3.org/1998/Math/MathML"
  xmlns:css="http://www.w3.org/1996/css" 
  xmlns:saxon="http://saxon.sf.net/"
  xmlns:xlink="http://www.w3.org/1999/xlink" 
  xmlns:jats="http://jats.nlm.nih.gov"
  xmlns:jats2html="http://transpect.io/jats2html" 
  xmlns:hub2htm="http://transpect.io/hub2htm" 
  xmlns:l10n="http://transpect.io/l10n"
  xmlns:tr="http://transpect.io" 
  xmlns:epub="http://www.idpf.org/2007/ops"
  xmlns:c="http://www.w3.org/ns/xproc-step"
  xmlns:cx="http://xmlcalabash.com/ns/extensions"
  xmlns:ali="http://www.niso.org/schemas/ali/1.0/"
  xmlns="http://www.w3.org/1999/xhtml"
  exclude-result-prefixes="ali c css cx epub html hub2htm jats jats2html l10n mml saxon tr xlink xs"
  version="2.0">

  <!-- If you see a message that an attribute cannot be created after a child of the containing
    element, see which 'unhandled' message comes before it and write a template for the unhandled. -->

  <!-- If you see a message telling you that something is unhandled, there is probably an xsl:next-match
       without a handler for it. You might add the element name to the matching pattern below 
       (search for 'Default handler')-->

  <xsl:import href="http://transpect.io/hub2html/xsl/css-rules.xsl"/>
  <xsl:import href="http://transpect.io/hub2html/xsl/css-atts2wrap.xsl"/>
  <xsl:import href="http://transpect.io/xslt-util/lengths/xsl/lengths.xsl"/>
  <xsl:import href="http://transpect.io/xslt-util/hex/xsl/hex.xsl"/>
  <xsl:import href="http://transpect.io/xslt-util/iso-lang/xsl/iso-lang.xsl"/>
  <xsl:import href="http://transpect.io/xslt-util/flat-list-to-tree/xsl/flat-list-to-tree.xsl"/>
  <xsl:import href="http://transpect.io/unwrap-mml/xsl/unwrap-mml.xsl"/>
	
  <xsl:param name="debug" select="'yes'" as="xs:string"/>
  <xsl:param name="debug-dir-uri" select="'debug'" as="xs:string"/>
  <xsl:param name="srcpaths" select="'no'" as="xs:string"/>
  <xsl:param name="create-metadata-head" select="'yes'" as="xs:string"/>
  <xsl:param name="render-metadata" select="'no'" as="xs:string"/>
  <!-- supported values: '1.0', '5.0' -->
  <xsl:param name="xhtml-version" select="'1.0'" as="xs:string"/>
  <!-- if xhtml-version is set to '5.0' and value here is 'yes', the footnotes are set as endnotes -->
  <xsl:param name="default-container-name" select="if($xhtml-version eq '5.0') then 'section' else 'div'" as="xs:string"/>
  <xsl:param name="toc" select="'no'" as="xs:string"/>
  <xsl:param name="toc-hidden" as="xs:string" select="'no'"/>
  <xsl:param name="toc-max-level" as="xs:integer?"/>
  <xsl:param name="bibliography-as-list" as="xs:string?" select="'no'"/>
  <xsl:param name="copy-colwidths" as="xs:string" select="'yes'">
    <!-- whether to repeat CSS widths in the first table rows in order to overcome bugs in ADE and others.
      But there are other bugs that may show if repeating the widths (table cell contents cut off to the right).
      See https://redmine.le-tex.de/issues/8516 for the problem that was addressed and https://redmine.le-tex.de/issues/8558
      for the problem that this fix created. -->
  </xsl:param>

  <xsl:param name="s9y1-path" as="xs:string?"/>
  <xsl:param name="s9y2-path" as="xs:string?"/>
  <xsl:param name="s9y3-path" as="xs:string?"/>
  <xsl:param name="s9y4-path" as="xs:string?"/>
  <xsl:param name="s9y5-path" as="xs:string?"/>
  <xsl:param name="s9y6-path" as="xs:string?"/>
  <xsl:param name="s9y7-path" as="xs:string?"/>
  <xsl:param name="s9y8-path" as="xs:string?"/>
  <xsl:param name="s9y9-path" as="xs:string?"/>
  <xsl:param name="s9y1-role" as="xs:string?"/>
  <xsl:param name="s9y2-role" as="xs:string?"/>
  <xsl:param name="s9y3-role" as="xs:string?"/>
  <xsl:param name="s9y4-role" as="xs:string?"/>
  <xsl:param name="s9y5-role" as="xs:string?"/>
  <xsl:param name="s9y6-role" as="xs:string?"/>
  <xsl:param name="s9y7-role" as="xs:string?"/>
  <xsl:param name="s9y8-role" as="xs:string?"/>
  <xsl:param name="s9y9-role" as="xs:string?"/>
  
  <xsl:variable name="paths" as="xs:string*" 
    select="($s9y1-path, $s9y2-path, $s9y3-path, $s9y4-path, $s9y5-path, $s9y6-path, $s9y7-path, $s9y8-path, $s9y9-path)"/>
  <xsl:variable name="roles" as="xs:string*" 
    select="($s9y1-role, $s9y2-role, $s9y3-role, $s9y4-role, $s9y5-role, $s9y6-role, $s9y7-role, $s9y8-role, $s9y9-role)"/>
  <xsl:variable name="common-path" as="xs:string?" select="$paths[position() = index-of($roles, 'common')]"/>
  <xsl:variable name="work-path" as="xs:string?" select="$paths[position() = index-of($roles, 'work')]"/>
  <xsl:variable name="publisher-path" as="xs:string?" select="$paths[position() = index-of($roles, 'publisher')]"/>
  <xsl:variable name="series-path" as="xs:string?" select="$paths[position() = index-of($roles, 'production-line')]"/>
  
  <xsl:param name="subtitles-in-titles" select="'yes'"/>
  <xsl:param name="authors-in-titles" select="'no'"/>
  <!-- with $xhtml-version eq '5.0' <section> will be created instead of <div> -->
  <xsl:param name="divify-sections" select="'no'"/>
  <xsl:param name="divify-title-groups" select="'no'"/>
  <!-- Resolve Relative links to the parent directory against the following URI
       (for example, the source XML directory's URL in the code repository),
       empty string or unset param if no resolution required: -->
  <xsl:param name="rr" select="'doc/'"/>
  <!-- convention: if empty string, then concat($common-path, '/css/stylesheet.css') -->
  <xsl:param name="css-location" select="''" as="xs:string?"/>
  <!-- for calculating whether a table covers the whole width or only part of it: -->
  <xsl:param name="page-width" 
             select="if (/book/book-meta/custom-meta-group/custom-meta[meta-name[. = 'type-area-width']]
                                                                      [matches(meta-value, '\d')]) 
                     then concat(((/book/book-meta/custom-meta-group/custom-meta[meta-name[. = 'type-area-width']]/meta-value) * 0.3527), 'mm')
                     else '180mm'"/>
  <xsl:param name="page-width-twips" select="tr:length-to-unitless-twip($page-width)" as="xs:double"/>
  <!-- whether to create backlinks from index terms to index entries.
       text-and-number: link from index terms with their text and number
       number: link from index terms with their number
       none: go figure -->
  <xsl:param name="index-backlink-type" select="'text-and-number'"/>   
  <!-- whether to link from bibliography entries to citations in the text.
       letter: link from entry with a letter
       none: go figure -->
  <xsl:param name="bib-backlink-type" select="'letter'"/>
  <!-- numbering consecutively <ref> entries in case <label> doesn't exists -->
  <xsl:param name="number-bibliography" select="'no'" as="xs:string"/>
  <!-- change markup for indices -->
  <xsl:param name="index-symbol-heading"   as="xs:string"  select="'0'"/>
  <xsl:param name="index-generate-title"   as="xs:string"  select="'no'"/>
  <xsl:param name="index-fallback-title"   as="xs:string"  select="'Index'"/>
  <xsl:param name="index-heading-elt-name" as="xs:string"  select="'h4'"/>
  <xsl:param name="index-heading-class"    as="xs:string"  select="'index-subheading'"/>
  <!-- position of table captions. Permitted values are: 'top' or 'bottom' -->
  <xsl:param name="table-caption-side"     as="xs:string"  select="'top'"/>
  <!-- Generates a footnote title element. This parameter applies only to generated footnote 
       sections. The title of an existing <fn-group> is rendered anyways. 
       For XHTML5 (EPUB3) output, the title is omitted generally, because the footnotes
       are typically rendered as popup-windows in the content.
  -->
  <xsl:param name="generate-footnote-title" select="'yes'" as="xs:string"/>
  <xsl:param name="footnote-title" as="xs:string" 
    select="     if($lang eq 'de') then 'Anmerkungen'
            else if($lang eq 'fr') then 'Notes'
            else if($lang eq 'es') then 'Notas'
            else if($lang eq 'pl') then 'Przypisy'
            else if($lang eq 'cz') then 'Vysvětlivky'
            else                        'Notes'"/>
  <xsl:param name="footnote-title-element-name" select="'h1'" as="xs:string"/>
  <xsl:param name="epub-version" as="xs:string" select="'EPUB3'"/>
  <xsl:param name="jats2html:create-loi" select="false()" as="xs:boolean"/>
  <xsl:param name="jats2html:create-lot" select="false()" as="xs:boolean"/>
  <xsl:param name="jats2html:loi-as-nav" select="false()" as="xs:boolean"/>
  <xsl:param name="jats2html:lot-as-nav" select="false()" as="xs:boolean"/>
  <xsl:param name="lot-as-nav" select="false()" as="xs:boolean"/>
  <xsl:param name="img-presentation-role" select="'tr_ARTIFACT'" as="xs:string"/>
  
  <xsl:output method="xhtml" indent="no" 
    doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"
    doctype-public="-//W3C//DTD XHTML 1.0//EN" 
    saxon:suppress-indentation="p li h1 h2 h3 h4 h5 h6 th td dd dt"/>
  
  <xsl:output method="xml" indent="yes" name="debug" exclude-result-prefixes="#all"/>

  <xsl:param name="lang" select="(/*/@xml:lang, 'en')[1]" as="xs:string"/>
  
  <xsl:variable name="l10n" select="document(concat('../l10n/l10n.', ($lang, 'en')[1], '.xml'))"
    as="document-node(element(l10n:l10n))"/>
  
  <xsl:key name="l10n-string" match="l10n:string" use="@id"/>

  <xsl:template match="html:img[not($epub-version = 'EPUB2')][(.|ancestor::html:div[contains(@class, 'fig')])/@class[1][matches(., $img-presentation-role)]]/@srcpath" 
    mode="clean-up" priority="7">
    <xsl:next-match/>
    <xsl:attribute name="role" select="'presentation'"/>
  </xsl:template>
  
  <xsl:template match="* | @*" mode="expand-css clean-up table-widths epub-alternatives">
    <xsl:copy copy-namespaces="no">
      <xsl:apply-templates select="@* | node()" mode="#current" />  
    </xsl:copy>
  </xsl:template>

  <xsl:template match="processing-instruction('break')" mode="epub-alternatives">
    <xsl:copy/>
  </xsl:template>
  
  <!-- collateral. Otherwise the generated IDs might differ due to temporary trees / variables 
    when transforming the content -->  
  <xsl:template match="*[name() = ('index-term', 'xref', 'fn')][not(@id)]" mode="epub-alternatives">
    <xsl:copy copy-namespaces="no">
      <xsl:attribute name="id" select="generate-id()"/>
      <xsl:apply-templates select="@*, node()" mode="#current"/>
    </xsl:copy>
  </xsl:template>
  
  <!-- render table footnotes below the table and do not include them into 
       the regular footnote listing as they're usually have another numbering anyways -->
  
  <xsl:template match="table-wrap-foot/fn-group" mode="epub-alternatives">
    <xsl:apply-templates mode="#current"/>
  </xsl:template>
  
  <xsl:template match="table-wrap-foot/fn-group/fn" mode="epub-alternatives">
    <div class="{local-name()}">
      <xsl:apply-templates select="@*, node()" mode="#current"/>
    </div>
  </xsl:template>  

  <xsl:template match="html:span[not(@* except @srcpath)]
                      |html:a[not(@* except @srcpath)]" mode="clean-up">
    <xsl:apply-templates mode="#current"/>
  </xsl:template>
  
  <xsl:template match="html:p//html:div" mode="clean-up">
    <span>
      <xsl:apply-templates select="@*, node()" mode="#current"/>
    </span>
  </xsl:template>

  <xsl:template match="*" mode="jats2html" priority="-1">
    <xsl:if test="$debug eq 'yes' and not(self::html:*)">
      <xsl:message>jats2html: unhandled: <xsl:apply-templates select="." mode="css:unhandled"/></xsl:message>
    </xsl:if>
    <xsl:copy>
      <xsl:apply-templates select="@* | node()" mode="#current" />  
    </xsl:copy>
  </xsl:template>
  
  <xsl:template match="@*" mode="jats2html">
    <xsl:if test="$debug eq 'yes'">
      <!--<xsl:message>jats2html: unhandled attr: <xsl:apply-templates select="." mode="css:unhandled"/></xsl:message>-->
    </xsl:if>
  </xsl:template>
  
  <xsl:template match="@dtd-version" mode="jats2html" />
  
  <!-- A customizing of the following template may look like this:
  <xsl:template match="/*" mode="jats2html">
    <xsl:next-match>
      <xsl:with-param name="footnote-roots" tunnel="yes" 
        select="//(
                   book-part[not(every $c in body/* satisfies $c/self::book-part)]
                  |front-matter-part | foreword | preface | dedication[book-part-meta/title-group/node()]
                  |named-book-part-body
                  |body[not(descendant::body)] |  named-book-part-body | glossary | title-group | front-matter
                  |book/book-back/ref-list | book/book-back/glossary | front-matter/ack
                  |app[empty(ancestor::app-group | ancestor::app)]
                  |app-group
                  |index[$use-print-index]
                  )"/>
    </xsl:next-match>
  </xsl:template>
  List all matching patterns of templates that invoke jats2html:footnotes.
  jats2html:footnotes will make sure that no footnote div will be generated if all footnotes of the context element 
  are contained in a footnote root that is nested within the context element.
  -->
  
  <xsl:template match="/" mode="jats2html"> 
    <xsl:param name="footnote-roots" tunnel="yes" 
               select="*" as="element(*)*"/>
    <html>
      <xsl:namespace name="mml">http://www.w3.org/1998/Math/MathML</xsl:namespace>
      <xsl:namespace name="epub">http://www.idpf.org/2007/ops</xsl:namespace>
      <xsl:apply-templates select="*/@xml:*" mode="#current"/>
      <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
        <xsl:if test="*/@source-dir-uri">
          <meta name="source-dir-uri" content="{*/@source-dir-uri}"/>
        </xsl:if>
        <xsl:call-template name="include-stylesheets"/>
        <xsl:if test="$create-metadata-head eq 'yes'">
          <xsl:call-template name="create-meta-tags"/>  
        </xsl:if>
        <title>
          <xsl:apply-templates select="book/book-meta/book-title-group/book-title
                               |article/front/article-meta/title-group/article-title" mode="strip-indexterms-etc"/>
        </title>
        <xsl:apply-templates select=".//custom-meta-group/css:rules" mode="hub2htm:css"/>
      </head>
      <body>
        <!-- Commented out because this template needs to be called in the context of metadata elements:
          <xsl:if test="$render-metadata eq 'yes'">
          <xsl:call-template name="render-metadata-sections"/>
        </xsl:if>-->
        <xsl:if test="$toc eq 'yes'">
          <xsl:call-template name="toc">
            <xsl:with-param name="toc-max-level" select="$toc-max-level" as="xs:integer?"/>
          </xsl:call-template>
        </xsl:if>
        <xsl:apply-templates mode="#current">
          <xsl:with-param name="footnote-ids" select="//fn[jats2html:include-footnote(.)]/@id" as="xs:string*" tunnel="yes"/>
          <xsl:with-param name="root" select="root(*)" as="document-node()" tunnel="yes"/>
          <xsl:with-param name="footnote-roots" as="element(*)*" tunnel="yes" select="$footnote-roots"/>
        </xsl:apply-templates>
        <xsl:call-template name="create-loi"/>
        <xsl:call-template name="create-lot"/>
      </body>
    </html>
  </xsl:template>
  
  <xsl:template name="include-stylesheets">
    <xsl:choose>
      <xsl:when test="$css-location eq ''">
        <link rel="stylesheet" type="text/css" href="{concat($common-path, 'css/stylesheet.css')}"/>  
      </xsl:when>
      <xsl:otherwise>
        <link rel="stylesheet" type="text/css" href="{$css-location}"/>    
      </xsl:otherwise>
    </xsl:choose>
    <xsl:for-each select="reverse($paths[not(position() = index-of($roles, 'common'))])">
      <link rel="stylesheet" type="text/css" href="{concat(., 'css/overrides.css')}"/>
    </xsl:for-each>
  </xsl:template>
  
  <xsl:template match="article | book | book-part-wrapper" mode="jats2html">
    <xsl:apply-templates mode="#current"/>
  </xsl:template>
  
  <xsl:template match="book-meta
                      |collection-meta
                      |front/journal-meta
                      |front/article-meta" mode="jats2html">
    <xsl:element name="{$default-container-name}">
      <xsl:attribute name="class" select="local-name()"/>
      <xsl:apply-templates select="@*" mode="jats2html"/>
      <xsl:call-template name="create-title-pages"/>
      <xsl:call-template name="render-metadata-sections"/>
    </xsl:element>
  </xsl:template>
  
  <xsl:template match="book-part-meta[$divify-sections eq 'yes']" mode="jats2html">
    <div class="{local-name(), parent::book-part/@book-part-type}">
      <xsl:call-template name="render-metadata-sections"/>
      <xsl:apply-templates mode="#current"/>      
    </div>
  </xsl:template>
  
  <xsl:template match="book-part-meta" mode="jats2html">
    <xsl:call-template name="render-metadata-sections"/>
    <xsl:apply-templates mode="#current"/>
  </xsl:template>
  
  <xsl:template match="book-part-meta/*[not(self::title-group or self::contrib-group)]" mode="jats2html"/>
  
  <!-- override this if you want to specify which elements appear in what order -->
  <xsl:template name="create-title-pages">
    <xsl:apply-templates select="@*, node()" mode="jats2html-create-title"/>
  </xsl:template>
  
   <xsl:template match="abstract | ack | app | bio | boxed-text | notes | question | sec | trans-abstract" mode="epub-alternatives">
     <xsl:copy copy-namespaces="no">
       <xsl:variable name="sec-meta-elements" 
                     select="label, 
                             title, 
                             subtitle, 
                             alt-title, 
                             sec-meta " as="element()*"/>
       <!-- sec-meta elements are located in BITS as first child of the section, followed by the title. So we change the order here -->
       <xsl:apply-templates select="@*,
                                    $sec-meta-elements,
                                    node() 
                                    except $sec-meta-elements" mode="#current"/>
     </xsl:copy>
  </xsl:template>
  
  <xsl:template match="sec-meta" mode="epub-alternatives">
    <xsl:apply-templates select="node()" mode="#current"/>
  </xsl:template>
  
  <xsl:variable name="default-structural-containers" as="xs:string+"
                select="('author-notes',
                         'abstract',
                         'ack',
                         'app',
                         'app-group',
                         'back',
                         'body',
                         'book-app',
                         'book-app-group',
                         'book-back',
                         'book-body',
                         'book-part',
                         'book-meta',
                         'contrib-group',
                         'dedication',
                         'fn-group',
                         'fig-group',
                         'index-group',
                         'foreword',
                         'front',
                         'front-matter',
                         'front-matter-part',
                         'glossary',
                         'named-book-part-body',
                         'preface',
                         'ref-list',
                         'sec',
                         'dark-matter')"/>
  
  <xsl:template match="*[local-name() = $default-structural-containers]" mode="jats2html" priority="2">
    <xsl:apply-templates select="if(title) 
                                 then (node() except label) (: label is already processed in title template :) 
                                 else node() (: no title, we process all nodes :)" mode="#current"/>
  </xsl:template>
  
  <!-- everything that goes into a div (except footnote-like content): -->
  <xsl:template match="*[local-name() = $default-structural-containers]
                        [$divify-sections = 'yes']
                      |abstract
                      |verse-group" 
                mode="jats2html" priority="15">
    <xsl:element name="{if(local-name() = ('abstract', 'verse-group', 'contrib-group') or parent::book-part) 
                        then 'div' 
                        else 'section'}">
      <xsl:apply-templates select="@* except (@book-part-type|@sec-type|@content-type)" mode="#current"/>
      <xsl:if test="tr:create-epub-type-attribute(.)">
        <xsl:attribute name="epub:type" select="tr:create-epub-type-attribute(.)"/>
      </xsl:if>
      <xsl:apply-templates select="." mode="class-att"/>
      <xsl:next-match/>
    </xsl:element>
  </xsl:template>
  
  <xsl:variable name="default-title-containers" as="xs:string+" select="('book-title-group', 'title-group', 'toc-title-group')"/>
  
  <xsl:template match="*[local-name() = $default-title-containers]" 
                mode="jats2html" priority="3">
    <xsl:choose>
      <xsl:when test="$divify-title-groups = 'yes'">
        <div class="{local-name()}">
          <!-- <label> is already processed in template which matches <title> -->
          <xsl:apply-templates select="node() except label" mode="#current"/>
        </div>
      </xsl:when>
      <xsl:otherwise>
        <xsl:apply-templates select="node() except label" mode="#current"/>
      </xsl:otherwise>
    </xsl:choose>
   </xsl:template>
  
  <xsl:template match="*" mode="jats2html" priority="7">
    <xsl:param name="footnote-roots" as="element(*)*" tunnel="yes"/>
    <xsl:next-match/>
    <xsl:if test="exists(. intersect $footnote-roots) and not(//fn-group)">
      <xsl:call-template name="jats2html:footnotes"/>
    </xsl:if>
  </xsl:template>
  
  <xsl:template name="jats2html:footnotes">
    <xsl:param name="recount-footnotes" as="xs:boolean?" tunnel="yes"/>
    <xsl:param name="static-footnotes" as="xs:boolean?" tunnel="yes"/>
    <xsl:param name="footnote-roots" as="element(*)*" tunnel="yes"/>
    <xsl:param name="footnote-heading-class" select="'footnote-heading'" as="xs:string?" tunnel="yes"/>
    <xsl:variable name="context" as="element(*)" select="."/>
    <xsl:variable name="footnotes" 
                  select=".//fn[jats2html:include-footnote(.)][not(some $fnroot in ($footnote-roots intersect current()/descendant::*) 
                                    satisfies (exists($fnroot/descendant::* intersect .))
                                    )]" as="element(fn)*"/>
    <xsl:if test="exists($footnotes)">
      <xsl:element name="{$default-container-name}">
        <xsl:attribute name="class" select="'footnotes'"/>
        <xsl:attribute name="epub:type" select="'footnotes'"/>        
        <xsl:if test="$recount-footnotes">
          <xsl:processing-instruction name="recount" select="'yes'"/>
        </xsl:if>
        <xsl:if test="$generate-footnote-title eq 'yes'">
            <xsl:choose>
              <xsl:when test="title">
                <xsl:apply-templates select="title" mode="#current"/>
              </xsl:when>
              <xsl:otherwise>
                <xsl:element name="{$footnote-title-element-name}">
                  <xsl:if test="$footnote-heading-class != ''">
                    <xsl:attribute name="class" select="$footnote-heading-class"/>
                  </xsl:if>
                  <xsl:value-of select="$footnote-title"/>
                </xsl:element>
              </xsl:otherwise>
            </xsl:choose>
        </xsl:if>
        <!--<xsl:comment select="'ancestor: ', name(../..), '/', name(..),'/', name(), @*, '          ', count($footnote-roots intersect current()/descendant::*), ' ;; ',
          count(.//fn[some $fnr in ($footnote-roots intersect current()/descendant::*) 
                        satisfies (exists($fnr/descendant::* intersect .))]), for $f in .//fn return ('  :: ', $f/ancestor::*/name()), 
                        '  ++  ', $footnote-roots/name()"></xsl:comment>-->
        <xsl:apply-templates select="$footnotes" mode="footnotes"/>
      </xsl:element>
    </xsl:if>
  </xsl:template>
  
  <xsl:template match="book-meta/*[local-name()= ('book-id', 'book-volume-id', 'isbn', 'permissions', 'book-volume-number', 'publisher')]" mode="jats2html">
    <div class="{local-name()}">
      <xsl:call-template name="css:content"/>
    </div>
  </xsl:template>

  
  <xsl:template match="subtitle | aff | attrib | license-p" mode="jats2html">
    <p class="{local-name()}">
      <xsl:call-template name="css:content"/>
    </p>
  </xsl:template>

  <xsl:template match="attrib[parent::*[name() = ('styled-content', 'named-content')]]" mode="jats2html" priority="2">
    <span class="{local-name()}">
      <xsl:call-template name="css:content"/>
    </span>
  </xsl:template>
  
  <xsl:template match="bio | permissions | license" mode="jats2html" >
    <div class="{local-name()}">
      <xsl:call-template name="css:content"/>
    </div>      
  </xsl:template>
  
  <xsl:template match="license/@xlink:href" mode="jats2html"/>
  
  <xsl:template match="copyright-holder
                      |copyright-statement
                      |copyright-year" mode="jats2html">
    <span class="{local-name()}">
      <xsl:call-template name="css:content"/>
    </span>
  </xsl:template>

  <xsl:template match="ali:free_to_read" mode="jats2html">
    <span class="ali">
      <xsl:value-of select="name()"/>
    </span>
  </xsl:template>

  <xsl:template match="contrib/string-name" mode="jats2html">
    <p class="author">
      <xsl:call-template name="css:content"/>
    </p>
  </xsl:template>

  <!-- Default handler for the content of para-like and phrase-like elements,
    invoked by an xsl:next-match for the same matching elements. Don't forget 
    to include the names of the elements that you want to handle here. Otherwise
    they'll be reported as unhandled.
    Most of these matching elements need to be synced with the default template 
    approx. 1400 lines down that creates
    <span class="{local-name()}">
      <xsl:next-match/>
    </span> 
    by default.
    And don’t ever change the priority unless you’ve made sure that no other template
    relies on this value to be 0.25.
    -->
  <xsl:template match="abbrev
                      |addr-line
                      |address
                      |answer
                      |array
                      |article-title
                      |attrib
                      |bold
                      |boxed-text
                      |chapter-title
                      |citation-alternatives
                      |city
                      |collab
                      |comment
                      |comment
                      |contrib
                      |contrib-id
                      |corresp
                      |country
                      |date
                      |day
                      |def
                      |degrees
                      |disp-formula
                      |disp-formula-group
                      |edition
                      |element-citation
                      |elocation-id
                      |equation-count
                      |etal
                      |explanation
                      |fig-count
                      |fpage
                      |funding-source
                      |funding-statement
                      |given-names
                      |gov
                      |hr
                      |inline-formula
                      |institution
                      |institution-wrap
                      |issue
                      |issue-id
                      |issue-part
                      |issue-title
                      |italic
                      |kwd
                      |label
                      |lpage
                      |mixed-citation
                      |monospace
                      |month
                      |name-alternatives
                      |named-content
                      |nav-pointer
                      |overline
                      |p
                      |page-range
                      |part-title
                      |patent
                      |person-group
                      |postal-code
                      |prefix
                      |private-char
                      |pub-id
                      |publisher-loc
                      |publisher-name
                      |question
                      |question-wrap
                      |related-article
                      |related-object
                      |role
                      |roman
                      |sans-serif
                      |season
                      |sc
                      |sig
                      |sig-block
                      |size
                      |series
                      |source
                      |speech
                      |state
                      |statement
                      |std
                      |strike
                      |string-date
                      |string-name
                      |styled-content
                      |sub
                      |subject
                      |subtitle
                      |suffix
                      |sup
                      |supplement
                      |surname
                      |table
                      |table-count
                      |term
                      |toc-entry
                      |trans-source
                      |trans-subtitle
                      |trans-title
                      |trans-title-group
                      |underline
                      |uri[not(@xlink:href)]
                      |verse-group
                      |verse-line
                      |volume
                      |volume-id
                      |volume-series
                      |year
                      |x" mode="jats2html" priority="-0.25">
    <xsl:call-template name="css:content"/>
  </xsl:template>
  
  <xsl:template name="css:other-atts" as="attribute(*)*">
    <!-- In the context of an element with CSSa attributes -->
    <xsl:apply-templates select="." mode="class-att"/>
    <xsl:call-template name="css:remaining-atts">
      <xsl:with-param name="remaining-atts" 
        select="@*[not(css:map-att-to-elt(., ..))]"/>
    </xsl:call-template>
  </xsl:template>

  <xsl:function name="jats2html:strip-combining" as="xs:string">
    <xsl:param name="input" as="xs:string"/>
    <xsl:sequence select="replace(normalize-unicode($input, 'NFKD'), '\p{Mn}', '')"/>
  </xsl:function>
  
  <xsl:template match="*" mode="class-att"/>

  <xsl:template match="*[@content-type | @style-type | @list-type | @list-content | @specific-use | 
                         @sec-type | @book-part-type]" mode="class-att" as="attribute(class)?" priority="15">
    <xsl:variable name="tokens" as="xs:string*">
      <xsl:apply-templates select="@content-type | @style-type | @list-type | @list-content | @specific-use | 
                                   @sec-type | @book-part-type" mode="#current"/>  
    </xsl:variable>
    <xsl:variable name="template-tokens" as="attribute()*">
      <xsl:next-match/>
    </xsl:variable>
    <xsl:if test="exists($tokens)">
      <xsl:attribute name="class" select="$template-tokens, $tokens" separator=" "/>
    </xsl:if>
  </xsl:template>

  <xsl:template match="@content-type | @list-content | @specific-use | 
                       @sec-type | @book-part-type" mode="class-att" as="attribute(class)">
    <xsl:attribute name="class" select="."/>
  </xsl:template>
  
  <xsl:template match="@list-type" mode="class-att" as="attribute(class)?">
    <xsl:if test="not(. = 'order')">
      <xsl:attribute name="class" 
                     select="if(matches(., '^(alpha|roman)-')) 
                             then string-join(reverse(tokenize(., '-')), '-')
                             else (parent::*/@css:list-style-type, .)[1]"/>  
    </xsl:if>
  </xsl:template>

  <xsl:template match="corresp|statement|question-wrap|question|answer|explanation|sig-block" mode="jats2html">
    <div>
      <xsl:next-match/>
    </div>
  </xsl:template>
  
  <xsl:template match="sig" mode="jats2html">
    <p class="{local-name()}">
      <xsl:next-match/>
    </p>
  </xsl:template>

  <xsl:template match="mixed-citation|element-citation|verse-line|fig" mode="class-att" priority="2"
     as="attribute(class)">
    <xsl:variable name="att" as="attribute(class)?">
      <xsl:next-match/>
    </xsl:variable>
    <!-- @specific-use could be 'PAGEBREAK', for ex. -->
    <xsl:attribute name="class" select="string-join((local-name(), @publication-type, @specific-use, $att), ' ')"/>
  </xsl:template>

  <xsl:template match="mixed-citation|element-citation|citation-alternatives" mode="jats2html" priority="3"> 
    <span class="{local-name()}">
      <xsl:next-match/>
    </span>
  </xsl:template>
  
  <xsl:variable name="citation-alternatives-output" 
    select="'rendered'" as="xs:string"/>

  <xsl:template match="citation-alternatives
                         [mixed-citation/@specific-use = 'rendered']
                         [element-citation]
                         /*[self::mixed-citation or self::element-citation]" 
    mode="jats2html" priority="5">
    <xsl:choose>
      <xsl:when test="self::element-citation and $citation-alternatives-output = 'rendered'"/>
      <xsl:when test="self::mixed-citation and $citation-alternatives-output = 'structured'"/>
      <xsl:otherwise>
        <xsl:next-match/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="mixed-citation" mode="jats2html" priority="4">
    <xsl:next-match/>
    <xsl:apply-templates select="../element-citation//target" mode="#current"/>
  </xsl:template>
  
  <xsl:variable name="jats2html:ignore-style-name-regex-x"
    select="'^(NormalParagraphStyle|Hyperlink)$'"
    as="xs:string"/>

  <xsl:template match="@content-type[not(../@style-type)] | @style-type" mode="class-att" as="attribute(class)?">
    <xsl:if test="not(matches(., $jats2html:ignore-style-name-regex-x, 'x'))">
      <xsl:attribute name="class" select="string-join((parent::*/local-name(),
                                                       replace(., ':', '_')), 
                                                      ' ')"/>  
    </xsl:if>
  </xsl:template>
  
  <xsl:template match="title[not($divify-sections = 'yes')]" mode="class-att" priority="2" as="attribute(class)">
    <xsl:attribute name="class" select="(parent::title-group[not(ends-with(../name(), 'meta'))],
                                         ancestor::*[ends-with(name(), 'meta')], 
                                         .)[1]/../
                                                 (name(), @book-part-type)[last()]"/>
  </xsl:template>
    
  <xsl:template match="label | speech | speaker | verse-group" mode="class-att" as="attribute(class)?">
    <xsl:attribute name="class" select="name()"/>
  </xsl:template>
  
  <xsl:template match="@srcpath" mode="jats2html jats2html-create-title">
    <xsl:if test="$srcpaths eq 'yes'">
      <xsl:copy/>  
    </xsl:if>
  </xsl:template>
  
  <xsl:template match="@id" mode="class-att jats2html">
    <xsl:copy/>
  </xsl:template>

  <xsl:template match="table[@id = ../@id]/@id" mode="jats2html"/>
  
  <xsl:template match="@css:*" mode="jats2html_DISABLED">
    <xsl:copy/>
  </xsl:template>
  
  <xsl:template match="@xml:lang" mode="jats2html jats2html-create-title">
    <xsl:copy-of select="."/>
    <xsl:attribute name="lang" select="."/>
    <xsl:if test="tr:is-valid-iso-lang-code(.)">
      <xsl:attribute name="dir" select="tr:lang-dir(.)"/>
    </xsl:if>
  </xsl:template>
  
  <xsl:template match="*[@dir]" mode="clean-up">
    <xsl:copy>
      <xsl:attribute name="class" select="concat(@class, ' ', @dir)"/>
      <xsl:apply-templates select="@* except @class, node()" mode="#current"/>
    </xsl:copy>
  </xsl:template>
  
  <xsl:template match="@xml:base" mode="jats2html jats2html-create-title">
    <xsl:attribute name="xml:base" select="replace(. , '\.[a-z]+$', '.html')"/>
  </xsl:template>
  
  <!-- will be handled by class-att mode -->
  <xsl:template match="@content-type | @style-type | @list-content | @specific-use" mode="jats2html"/>

  <xsl:template match="*[self::*:td|self::*:th]/@scope" mode="jats2html">
    <xsl:copy copy-namespaces="no"/>
  </xsl:template>
  
  <xsl:template match="contrib-id" mode="jats2html">
    <span class="{local-name()}">
      <xsl:next-match/>
    </span>
  </xsl:template>

  <!-- break-PI: hub2bits workaround -->
  <xsl:template match="break | processing-instruction('break')" mode="jats2html">
    <xsl:param name="in-toc" as="xs:boolean?"/>
    <xsl:if test="not($in-toc)">
      <br/>
    </xsl:if>
  </xsl:template>
  
  <xsl:template match="break[ancestor::*[self::*:book-title]]" priority="2" mode="jats2html">
    <xsl:choose>
    <xsl:when test="preceding-sibling::node()[1]/(self::text()) and matches(preceding-sibling::node()[1], '\s$') or
      following-sibling::node()[1]/(self::text()) and matches(following-sibling::node()[1], '^\s')"/>
      <xsl:otherwise><xsl:text>&#160;</xsl:text></xsl:otherwise>
    </xsl:choose>
  </xsl:template>
     
  <xsl:template match="target
                      |milestone-start" mode="jats2html" priority="1.5">
    <a class="{local-name()}" id="{(@id, generate-id())[1]}"/>
  </xsl:template>
  
  <xsl:template match="milestone-end" mode="jats2html">
    <a class="{local-name()}" href="#{(preceding::milestone-start[1]/@id, preceding::milestone-start[1]/generate-id())[1]}"/>
  </xsl:template>
  
  <xsl:template match="boxed-text[@content-type eq 'marginalia']" mode="jats2html">
    <div>
      <xsl:next-match/>
    </div>   
  </xsl:template>

  <xsl:template match="speech" mode="jats2html">
    <div>
      <xsl:call-template name="css:other-atts"/>
      <xsl:apply-templates select="p" mode="#current"/>
    </div>
  </xsl:template>
  
  <xsl:template match="speech/p" mode="jats2html">
    <p>
      <xsl:call-template name="css:other-atts"/>
      <xsl:apply-templates select="preceding-sibling::*[1]/self::speaker" mode="#current"/>
      <xsl:apply-templates select="node()" mode="#current"/>
    </p>   
  </xsl:template>
  
  <xsl:template match="speech/speaker" mode="jats2html">
    <span class="{local-name()}">
      <xsl:call-template name="css:content"/>
    </span>
    <xsl:text>&#xa;</xsl:text>
  </xsl:template>
  
  <xsl:template match="*[p[@specific-use eq 'EpubAlternative']]" mode="epub-alternatives" priority="2">
    <xsl:copy copy-namespaces="no">
      <xsl:apply-templates select="@*, title | info | p[@specific-use eq 'EpubAlternative']" mode="#current"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="permissions[preceding-sibling::*/p[@specific-use eq 'EpubAlternative']]" mode="epub-alternatives"
                priority="2"/>

  <xsl:template match="*[@specific-use eq 'EOnly']" mode="epub-alternatives" priority="2">
    <xsl:copy copy-namespaces="no">
        <xsl:apply-templates select="@*, title | info | node()" mode="#current"/> 
    </xsl:copy>
  </xsl:template>
  
  <xsl:template match="@specific-use[. = ('EpubAlternative', 'EOnly')]" mode="class-att"/>

  <xsl:template match="*[@specific-use eq 'PrintOnly']" mode="epub-alternatives" priority="2"/>
  
  <xsl:template match="table-wrap[exists(descendant::*[self::p])][every $child in .//p satisfies ($child/@specific-use = 'PrintOnly')]" mode="epub-alternatives"/>
  <xsl:template match="disp-quote[exists(descendant::*[self::p])][every $child in * satisfies ($child/@specific-use = 'PrintOnly')]" mode="epub-alternatives"/>

  <xsl:template match="*[fn]" mode="jats2html" priority="1">
    <xsl:next-match/>
  </xsl:template>

  <xsl:template match="fn[jats2html:include-footnote(.)][@id]" mode="footnotes">
    <xsl:param name="footnote-ids" tunnel="yes" as="xs:string*"/>
    <xsl:param name="static-footnotes" tunnel="yes" as="xs:boolean?"/>
    <xsl:variable name="index" select="index-of($footnote-ids, @id)[1]" as="xs:integer"/>
    <xsl:element name="{if($xhtml-version eq '5.0') then 'aside' else 'div'}">
      <xsl:attribute name="id" select="concat('fn_', $index)"/>
      <xsl:attribute name="class" select="'fn'"/>
      <xsl:copy-of select="@srcpath"/>
      <xsl:apply-templates select="." mode="epub-type"/>
      <span class="note-mark">
        <xsl:choose>
          <xsl:when test="$static-footnotes">
            <xsl:value-of select="(@symbol,label, $index)[1]"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:call-template name="footnote-link">
              <xsl:with-param name="index" select="$index" as="xs:integer"/>
            </xsl:call-template>
          </xsl:otherwise>
        </xsl:choose>
      </span>
      <xsl:apply-templates select="node() except label" mode="jats2html"/>
    </xsl:element>
  </xsl:template>
  
  <xsl:template name="footnote-link">
    <xsl:param name="footnote-ids" as="xs:string*" tunnel="yes"/>
    <xsl:param name="index" as="xs:integer"/>
    <a href="#fna_{$index}" class="fn-link">
      <xsl:if test="tr:create-epub-type-attribute(.)">
        <xsl:attribute name="epub:type" select="'noteref'"/>
      </xsl:if>
      <xsl:value-of select="(@symbol, $index)[1]"/>
    </a>
  </xsl:template>

  <xsl:template match="fn[jats2html:include-footnote(.)][@id]" mode="jats2html">
    <xsl:param name="footnote-ids" tunnel="yes" as="xs:string*"/>
    <xsl:param name="in-toc" tunnel="yes" as="xs:boolean?"/>
    <xsl:param name="recount-footnotes" tunnel="yes" as="xs:boolean?"/>
    <xsl:variable name="index" select="index-of($footnote-ids, @id)[1]" as="xs:integer?"/>
    <xsl:if test="empty($index) and not($in-toc)">
      <xsl:message select="'Could not find ', @id, ' in footnote IDs ', string-join($footnote-ids, ', ')" terminate="yes"/>
    </xsl:if>
    <xsl:if test="not($in-toc)">
      <span class="note-anchor" id="fna_{$index}">
        <xsl:apply-templates select="." mode="title-att"/>
        <xsl:if test="$recount-footnotes">
          <xsl:processing-instruction name="recount" select="'yes'"/>
        </xsl:if>
        <a href="#{concat('fn_', $index)}" class="fn-ref">
          <xsl:if test="tr:create-epub-type-attribute(.)">
            <xsl:attribute name="epub:type" select="'noteref'"/>
          </xsl:if>
          <sup>
            <xsl:value-of select="(@symbol, label, $index)[1]"/>
          </sup>
        </a>
      </span>    
    </xsl:if>
  </xsl:template>
  
  <xsl:template match="fn" mode="title-att">
    <xsl:variable name="tmp" as="node()*">
      <xsl:apply-templates mode="strip-indexterms-etc"/>
    </xsl:variable>
    <xsl:attribute name="title" select="normalize-space(string-join($tmp, ''))"/>
  </xsl:template>

  <xsl:template match="fn-group" mode="jats2html" priority="2.5">
    <xsl:call-template name="jats2html:footnotes">
      <xsl:with-param name="recount-footnotes" select="true()" as="xs:boolean?" tunnel="yes"/>
      <xsl:with-param name="footnote-ids" select=".//fn[jats2html:include-footnote(.)]/@id" as="xs:string*" tunnel="yes"/>
      <xsl:with-param name="static-footnotes" select="true()" as="xs:boolean?" tunnel="yes"/>
    </xsl:call-template>
  </xsl:template>

  <!-- var fn-type-exclusion-values to handle specific non-in-text footnotes, separately
       examples: coi-statement, financial-disclosure -->
  <xsl:variable name="fn-type-exclusion-values" as="xs:string*"
    select="('_unset_')"/>

  <xsl:function name="jats2html:include-footnote" as="xs:boolean">
    <xsl:param name="fn" as="element(fn)"/>
    <xsl:sequence select="if($fn/@fn-type = $fn-type-exclusion-values) then false() else true()"/>
  </xsl:function>
 
  <xsl:template match="xref[matches(@rid, '^(id_endnote|id_en-)')]" mode="jats2html" priority="5.1">
    <!-- endnote markers (from InDesign CC)-->
    <xsl:param name="in-toc" tunnel="yes" as="xs:boolean?"/>
    <xsl:if test="not($in-toc)">
      <sup>
        <xsl:next-match/>
      </sup>
    </xsl:if>
  </xsl:template>
  
  <xsl:template match="xref[@specific-use=('EndnoteMarker', 'EndnoteRange')][@rid]" 
    mode="jats2html" priority="6">
    <!-- InDesign CC endnotes from 2020-03 on -->
    <xsl:param name="in-toc" tunnel="yes" as="xs:boolean?"/>
    <xsl:if test="not($in-toc)">
      <sup>
        <a href="#{@rid}">
          <!-- avoid prefixing the id with 'xref_' since a link to this id was not adjusted accordingly.
          Therefore overriding this xref handling template. -->
          <xsl:copy-of select="@id"/>
          <xsl:if test="$epub-version = 'EPUB3'">
            <xsl:if test="@specific-use= 'EndnoteRange'"><xsl:attribute name="epub:type" select="'noteref'"/></xsl:if>
            <xsl:attribute name="role" select="if (@specific-use= 'EndnoteMarker') then 'doc-backlink' else 'doc-noteref'"/>
          </xsl:if>
          <xsl:apply-templates mode="#current"/>
        </a>
      </sup>
    </xsl:if>
  </xsl:template>

  <xsl:template match="target[starts-with(@id, 'id_endnote-')][. is ../node()[1]]" mode="jats2html" priority="5.25">
    <!-- endnote paras (from InDesign CC), as produced by idml2xml before 2020-03-06 -->
      <xsl:next-match/>
      <span class="endnote-anchor">
        <a href="#id_endnoteAnchor-{replace(@id, '^id_endnote-', '')}">
          <xsl:if test="$epub-version = 'EPUB3'">
            <xsl:attribute name="epub:type" select="'endnote'"/>
            <xsl:attribute name="role" select="'doc-backlink'"/>
          </xsl:if>
          <sup>
            <xsl:value-of select="replace(@id, '^id_endnote-', '')"/>
          </sup>
        </a>
      </span>
  </xsl:template>

  <xsl:template match="related-article[@xlink:href]" mode="jats2html">
    <a class="{local-name()}" href="{if(starts-with(@xlink:href , 'http')) then @xlink:href else concat('#', @xlink:href)}">
      <xsl:apply-templates select="@*, node()" mode="#current"/>
    </a>
  </xsl:template>
  
  <xsl:template match="ref-list[$bibliography-as-list = ('yes', 'true')]
                               [every $child in * satisfies $child[self::ref|self::label|self::title]]" mode="jats2html" priority="5">
    
    <section>
      <xsl:apply-templates select="." mode="class-att"/>
      <xsl:apply-templates select="title" mode="#current"/>
      <ul class="ref">
        <xsl:apply-templates select="@* except (@book-part-type|@sec-type|@content-type|@id)" mode="#current"/>
        <xsl:if test="tr:create-epub-type-attribute(.)">
          <xsl:attribute name="epub:type" select="tr:create-epub-type-attribute(.)"/>
        </xsl:if>
        <xsl:apply-templates select="node() except title" mode="#current">
          <xsl:with-param name="create-list-items" as="xs:boolean" select="true()" tunnel="yes"/>
        </xsl:apply-templates>
      </ul>
    </section>
  </xsl:template>
 
  <xsl:template match="ref-list[$bibliography-as-list = ('yes', 'true')]/ref" mode="jats2html" priority="5">
    <xsl:param name="create-list-items" as="xs:boolean?" tunnel="yes"/>
    <xsl:choose>
      <xsl:when test="$create-list-items">
        <li>
          <xsl:apply-templates select="@*, node()" mode="#current"/>
        </li>
      </xsl:when>
      <xsl:otherwise>
        <xsl:next-match/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="*[html:p[html:span[@class = 'endnote-anchor']]]" mode="clean-up" priority="5">
    <!-- group endnote paras (from InDesign CC)-->
    <xsl:copy copy-namespaces="no">
      <xsl:apply-templates select="@*" mode="#current"/>
      <xsl:element name="div">
        <xsl:attribute name="class" select="'endnotes'"/>
        <xsl:for-each-group select="node()" group-starting-with="html:p[html:span[@class = 'endnote-anchor']]">
          <xsl:choose>
            <xsl:when test="current-group()[self::html:p[html:span[@class = 'endnote-anchor']]]">
              <xsl:element name="div">
                <xsl:attribute name="class" select="'en'"/>
                <xsl:apply-templates select="current-group()[1]/html:a[. is ../*[1]]/@id, current-group()" mode="#current"/>
              </xsl:element>
            </xsl:when>
            <xsl:otherwise>
              <xsl:apply-templates select="current-group()" mode="#current"/>
            </xsl:otherwise>
          </xsl:choose>
        </xsl:for-each-group>
      </xsl:element>
    </xsl:copy>
  </xsl:template>
  
  <xsl:template match="html:p[html:span[@class = 'endnote-anchor']]" mode="clean-up" priority="5">
    <xsl:apply-templates select="html:span[@class = 'endnote-anchor']" mode="#current"/>
    <xsl:copy copy-namespaces="no">
      <xsl:apply-templates select="@*, node() except (*[1][self::html:a], html:span[@class = 'endnote-anchor'])" mode="#current"/>
    </xsl:copy>
  </xsl:template>
      
	<xsl:template match="p[@specific-use = ('itemizedlist', 'orderedlist', 'variablelist')]" mode="jats2html">
    <xsl:apply-templates mode="#current">
      <xsl:with-param name="former-list-type" as="xs:string" select="@specific-use"/>
    </xsl:apply-templates>
  </xsl:template>
  
  <xsl:template match="def-list/title" mode="jats2html"/>
  
  <xsl:template match="def-list/title" mode="move-def-list-title">
    <xsl:element name="{concat('h', jats2html:heading-level(.))}">
      <xsl:apply-templates select="@*, node()" mode="jats2html"/>  
    </xsl:element>
  </xsl:template>
  
  <xsl:template match="def-list" mode="jats2html">
    <xsl:param name="former-list-type" as="xs:string?"/>
    <xsl:apply-templates select="title" mode="move-def-list-title"/>
    <xsl:choose>
      <xsl:when test="(($former-list-type = 'itemizedlist') 
                       and (every $term in def-item/term 
                            satisfies $term = def-item[1]/term))
                       or not(.//def) or not(.//term)">
        <ul>
          <xsl:call-template name="css:content">
            <xsl:with-param name="discard-term" as="xs:boolean" 
                            select="if (normalize-space($former-list-type) or not(.//term)) 
                                    then true() 
                                    else false()" tunnel="yes"/>
            <xsl:with-param name="discard-def" as="xs:boolean" 
                            select="not(.//def)" tunnel="yes"/>
          </xsl:call-template>
        </ul>
      </xsl:when>
      <xsl:when test="($former-list-type = 'orderedlist') and (matches(def-item[1]/term, '^[1a]\.$'))">
        <ol>
          <xsl:call-template name="css:content">
            <xsl:with-param name="discard-term" as="xs:boolean" 
                                  select="if (normalize-space($former-list-type)) 
                                          then true() 
                                          else false()" tunnel="yes"/>
          </xsl:call-template>
        </ol>
      </xsl:when>
      <xsl:otherwise>
        <dl>
          <xsl:call-template name="css:content"/>
        </dl>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
    
  <xsl:template match="def-item" mode="jats2html">
    <xsl:apply-templates mode="#current"/>
  </xsl:template>
  
  <xsl:template match="def-item/@id" mode="jats2html">
    <a>
      <xsl:next-match/>
    </a>
  </xsl:template>

  <xsl:template match="def-item/term" mode="jats2html">
    <xsl:param name="discard-term" as="xs:boolean?" tunnel="yes"/>
    <xsl:param name="discard-def" as="xs:boolean?" tunnel="yes"/>
    <xsl:choose>
      <xsl:when test="not($discard-term) and not($discard-def)">
        <dt>
          <xsl:apply-templates select=".." mode="class-att"/>
          <xsl:next-match/><!-- typically css:content -->
          <xsl:apply-templates select="../@id" mode="#current"/>
        </dt>
      </xsl:when>
      <xsl:when test="$discard-def">
        <li>
          <xsl:apply-templates select=".." mode="class-att"/>
          <xsl:next-match/>
          <xsl:apply-templates select="../@id" mode="#current"/>
        </li>
      </xsl:when>
    </xsl:choose>
  </xsl:template>
  
  <xsl:template match="def-list/def-list" mode="jats2html"/>
  
  <xsl:template match="def-item/def" mode="jats2html">
    <xsl:param name="discard-term" as="xs:boolean?" tunnel="yes"/>
    <xsl:variable name="following-nested-def-list" as="element(def-list)?">
      <xsl:copy-of select="parent::def-item/following-sibling::*[1][self::def-list]"/>
    </xsl:variable>
    <xsl:if test="not(($discard-term)) and not(parent::def-item/term)">
      <dt/>
    </xsl:if>
    <xsl:element name="{if ($discard-term) then 'li' else 'dd'}">
      <xsl:apply-templates select=".." mode="class-att"/>
      <xsl:next-match/>
      <xsl:apply-templates select="$following-nested-def-list" mode="#current"/>
    </xsl:element>
  </xsl:template>
  
  <xsl:template match="glossary/def-list/def-item/term" mode="jats2html" priority="-0.2">
    <xsl:apply-templates select="." mode="epub-type"/>
    <xsl:apply-templates select=".." mode="class-att"/>
    <xsl:next-match/><!-- should be css:content -->
  </xsl:template>
  
  <xsl:template match="glossary/def-list/def-item/term" mode="epub-type">
    <xsl:attribute name="epub:type" select="'glossterm'"/>
  </xsl:template>
  
  <xsl:template match="glossary/def-list/def-item/def" mode="jats2html" priority="-0.2">
    <xsl:apply-templates select="." mode="epub-type"/>
    <xsl:apply-templates select=".." mode="class-att"/>
    <xsl:next-match/><!-- should be css:content -->
  </xsl:template>
  
  <xsl:template match="glossary/def-list/def-item/def" mode="epub-type">
    <xsl:attribute name="epub:type" select="'glossdef'"/>
  </xsl:template>
  
  <xsl:template match="def-item/def|def-item/term" mode="jats2html" priority="-0.75">
    <xsl:apply-templates mode="#current"/>
  </xsl:template>

  <xsl:template match="*:dd/*:label
                      |html:ul/html:span" mode="clean-up"/>
  
  <xsl:template match="html:li[preceding-sibling::*[1][self::html:span]]" mode="clean-up">
    <xsl:copy>
      <span class="label">
        <xsl:apply-templates select="preceding-sibling::*[1][self::html:span]/node()" mode="#current"/>
        <xsl:text>&#x20;</xsl:text>
      </span>
      <xsl:apply-templates mode="#current"/>
    </xsl:copy>
  </xsl:template>
  
  <xsl:template match="list[title]" mode="jats2html" priority="5">
    <xsl:apply-templates select="title" mode="#current"/>
    <xsl:next-match/>
  </xsl:template>
  
  <xsl:template match="list[not(matches(@list-type, '^(order|alpha|roman|alpha-lower|alpha-upper|roman-lower|roman-upper)$')) 
                            or not(@list-type)]" 
                mode="jats2html">
    <ul>
      <xsl:apply-templates select="@*" mode="#current"/>
      <xsl:apply-templates select="." mode="class-att"/>
      <xsl:apply-templates select="node() except title" mode="#current"/>
    </ul>
  </xsl:template>
  
  <xsl:template match="list[matches(@list-type, '^(order|alpha|roman|alpha-lower|alpha-upper|roman-lower|roman-upper)$')]" 
                mode="jats2html">
    <ol>
      <xsl:call-template name="css:content"/>
    </ol>
  </xsl:template>
  
  <xsl:template match="list[@list-type eq 'custom'][list-item[label]]" mode="jats2html">
    <dl>
      <xsl:apply-templates select="@*, node() except title" mode="#current"/>
    </dl>
  </xsl:template>
  
  <xsl:template match="list[@list-type eq 'custom']/list-item" mode="jats2html">
    <dt>
      <xsl:apply-templates select="label" mode="#current"/>
    </dt>
    <dd>
      <xsl:apply-templates select="@*, node() except label" mode="#current"/>
    </dd>
  </xsl:template>
  
  <xsl:template match="list-item" mode="jats2html">
    <li>
      <xsl:call-template name="css:content"/>
    </li>
  </xsl:template>
  
  <xsl:template match="preformat" mode="jats2html">
    <pre>
      <xsl:call-template name="css:content"/>
    </pre>
  </xsl:template>
  
  <xsl:template match="code" mode="jats2html">
    <pre><code class="{string-join(for $i in @* except @srcpath
                                   return concat($i/local-name(), '_', $i), ' ')}">
      <xsl:call-template name="css:content"/>
    </code></pre>
  </xsl:template>

  <xsl:template match="disp-quote" mode="jats2html">
    <blockquote>
      <xsl:call-template name="css:content"/>
    </blockquote>
  </xsl:template>
  
  <!-- please note that <notes> can include notes 
       which may represent notes from editors or other notabilities
       and shouldn't be confused with general notes or footnotes, 
       although this element can appear notelessly in the regular content. -->
  
  <xsl:template match="notes" mode="jats2html">
    <div>
      <xsl:attribute name="class" select="string-join((local-name(), @notes-type), ' ')"/>
      <xsl:call-template name="css:content"/>
    </div>
  </xsl:template>
  
  <xsl:template match="front-matter/notes" mode="jats2html">
    <xsl:element name="{$default-container-name}">
      <xsl:attribute name="class" select="local-name()"/>
      <xsl:apply-templates select="@*, node()" mode="#current"/>
    </xsl:element>
  </xsl:template>
  
  <xsl:template match="option" mode="jats2html">
    <div class="{local-name(), if(@correct) then concat('correct-', @correct) else ()}">
      <xsl:call-template name="css:content"/>
    </div>
  </xsl:template>
  
  <xsl:template match="floats-group" mode="jats2html">
    <div class="{local-name()}">
      <xsl:apply-templates select="@*, node()" mode="#current"/>
    </div>
  </xsl:template>
  
  <xsl:template match="fig" mode="jats2html">
    <xsl:element name="{if($xhtml-version eq '5.0') then 'figure' else 'div'}">
      <xsl:attribute name="class" select="string-join((name(), @book-part-type, @sec-type, @content-type), ' ')"/>  
      <xsl:call-template name="css:other-atts"/>
      <xsl:if test="$jats2html:create-loi and not(@id)">
        <!-- iffig has no @id but a list of figures is created: add @id-->
        <xsl:attribute name="id" select="generate-id(.)"/>
      </xsl:if>
      <xsl:apply-templates select="* except (label | caption | permissions), caption" mode="#current"/>
    </xsl:element>
  </xsl:template>
    
  <xsl:template match="fig/caption[$xhtml-version eq '5.0']
                      |graphic/caption[$xhtml-version eq '5.0']" mode="jats2html" priority="8">
    <figcaption>
      <xsl:attribute name="class" select="string-join((name(), @book-part-type, @sec-type, @content-type), ' ')"/>
      <xsl:apply-templates select="@*" mode="#current"/>
      <xsl:if test="../label">
        <p>
          <xsl:apply-templates select="../label" mode="#current"/>
          <xsl:text>&#x20;</xsl:text>
          <xsl:apply-templates select="*[1]/node()" mode="#current"/>
        </p>
      </xsl:if>
      <xsl:apply-templates select="if(../label) then *[not(position() eq 1)] else node(), 
                                   ../permissions" mode="#current"/>
    </figcaption>
  </xsl:template>
  
  <xsl:template match="caption" mode="jats2html">
    <div>
      <xsl:attribute name="class" select="string-join(
                                            (
                                              name(), 
                                              @book-part-type, @sec-type, @content-type, 
                                              if(
                                                normalize-space(title) = ''
                                                and 
                                                normalize-space(../label) = ''
                                              ) 
                                              then 'empty-title' 
                                              else ''
                                            )[. != ''],
                                            ' ')"/>
      <xsl:call-template name="css:content"/>
    </div>
  </xsl:template>

  <xsl:template match="table-wrap|table-wrap-foot" mode="jats2html">
    <xsl:variable name="table-caption" as="element()">
      <div class="table-caption caption">
        <xsl:if test="label">
          <p>
            <xsl:apply-templates select="label, caption/*[1]/node()" mode="#current"/>
          </p>
        </xsl:if>
        <xsl:apply-templates select="if (label) then caption/*[position() ne 1] else caption" mode="#current"/>
      </div>
    </xsl:variable>
    <div class="{local-name()} {distinct-values(for $ct in (@content-type, table/@content-type, if (alternatives) then 'alt-image' else ()) return tokenize($ct, '\s+'))}">
      <xsl:apply-templates select="@*" mode="#current"/>
      <xsl:if test="self::table-wrap and $jats2html:create-lot and not(@id)">
        <!-- if table-wrap has no @id but a list of tables is created: add @id-->
        <xsl:attribute name="id" select="generate-id(.)"/>
      </xsl:if>
      <xsl:if test="(label|caption) and $table-caption-side eq 'top'">
        <xsl:sequence select="$table-caption"/>
      </xsl:if>
      <xsl:apply-templates select="* except (label|caption|table[..[alternatives]])" mode="#current"/>
      <xsl:if test="(label|caption) and $table-caption-side eq 'bottom'">
        <xsl:sequence select="$table-caption"/>
      </xsl:if>
    </div>
  </xsl:template>

  <!-- special case when alternative images is rendered for epub-->  
<!--  <xsl:template match="table-wrap[alternatives]" mode="jats2html" priority="3">
    <div class="{local-name()} {distinct-values(table/@content-type)} alt-image">
      <xsl:apply-templates select="@*, node() except table" mode="#current"/>
    </div>
  </xsl:template>-->
  
  <xsl:template match="@preformat-type" mode="jats2html">
    <xsl:attribute name="class" select="."/>
  </xsl:template>
  
  <xsl:variable name="frontmatter-parts" as="xs:string+" 
                select="('title-page', 
                         'frontispiz', 
                         'copyright-page', 
                         'about-contrib', 
                         'about-book', 
                         'series', 
                         'additional-info')"/>
  
  <xsl:template match="pb" mode="epub-type">
    <xsl:attribute name="epub:type" select="'pagebreak'"/>
  </xsl:template>
  
  <xsl:template match="ack" mode="epub-type">
    <xsl:attribute name="epub:type" select="'acknowledgments'"/>
  </xsl:template>
  
  <xsl:template match="bio" mode="epub-type">
    <xsl:attribute name="epub:type" select="'contributors'"/>
  </xsl:template>
  
  <xsl:template match="ref-list" mode="epub-type">
    <xsl:attribute name="epub:type" select="'bibliography'"/>
  </xsl:template>
  
  <xsl:template match="ref" mode="epub-type">
    <xsl:attribute name="epub:type" select="'biblioentry'"/>
  </xsl:template>
  
  <xsl:template match="*[local-name() = ('preface')]
                        [matches(*:book-part-meta/*:title-group/*:title, '(Introduction|Einleitung|Einführung)')]" 
                mode="epub-type" priority="1">
    <xsl:attribute name="epub:type" select="'introduction'"/>
  </xsl:template>
  
  <xsl:template match="*[local-name() = ('preface', 'foreword', 'dedication', 'glossary', 'index', 'index-term', 'toc')]" mode="epub-type">
    <xsl:attribute name="epub:type" select="local-name()"/>
  </xsl:template>
 
  <xsl:template match="front-matter-part[@book-part-type = 'copyright-page']" mode="epub-type">
    <xsl:attribute name="epub:type" select="@book-part-type"/>
  </xsl:template>
  
  <xsl:template match="front-matter-part[@book-part-type = 'title-page']" mode="epub-type">
    <xsl:attribute name="epub:type" select="translate(@book-part-type, '-', '')"/>
  </xsl:template>
  
  <xsl:template match="book-part[@book-part-type]" mode="epub-type">
    <xsl:attribute name="epub:type" select="@book-part-type"/>
  </xsl:template>
  
  <xsl:template match="book-back[@book-part-type]" mode="epub-type">
    <xsl:attribute name="epub:type" select="@book-part-type"/>
  </xsl:template>
  
  <xsl:template match="app | book-app" mode="epub-type">
    <xsl:attribute name="epub:type" select="'appendix'"/>
  </xsl:template>
  
  <xsl:template match="notes | fn-group" mode="epub-type">
    <xsl:attribute name="epub:type" select="'footnotes'"/>
  </xsl:template>
  
  <xsl:template match="fn" mode="epub-type">
    <xsl:attribute name="epub:type" select="'footnote'"/>
  </xsl:template>
  
  <xsl:template match="front-matter" mode="epub-type">
    <xsl:attribute name="epub:type" select="'frontmatter'"/>
  </xsl:template>
  
  <xsl:template match="book-body" mode="epub-type">
    <xsl:attribute name="epub:type" select="'bodymatter'"/>
  </xsl:template>
  
  <xsl:template match="book-back" mode="epub-type">
    <xsl:attribute name="epub:type" select="'backmatter'"/>
  </xsl:template>
  
  <xsl:template match="xref[key('by-id', @rid)[self::mixed-citation|self::ref|self::element-citation]]" mode="epub-type">
    <xsl:attribute name="epub:type" select="'biblioref'"/>
  </xsl:template>
  
  <xsl:template match="*" mode="epub-type"/>

  <xsl:function name="tr:create-epub-type-attribute" as="attribute()?">
    <xsl:param name="context" as="element(*)"/>
    <xsl:apply-templates select="$context" mode="epub-type"/>
   </xsl:function>
  
  <xsl:variable name="jats2html:notoc-regex" as="xs:string" select="'_-_NOTOC'">
    <!-- Overwrite this regex in your adaptions to exclude titles containing this string in its content-type from being listed in the html toc -->
  </xsl:variable>
  
  <xsl:variable name="jats2html:toc-headlines" as="element()*"
                select="//*[self::title or self::label[parent::sec[not(title)] or title-group[not(title)]]]
                           [parent::sec[not(ancestor::boxed-text)]
                           |parent::title-group
                           |parent::app
                           |parent::ack
                           |parent::index-title-group
                           |parent::app-group
                           |parent::ref-list
                           |parent::glossary]
                           [not(   ancestor::boxed-text 
                                or ancestor::toc 
                                or ancestor::collection-meta
                                or ancestor::book-meta
                                or ancestor::index-div)]
                           [jats2html:heading-level(.) le number((current()/@depth, 100)[1]) + 1]
                           [not(matches(@content-type, $jats2html:notoc-regex))]"/>
  
  <!-- if no toc element is given, you can also invoke this with <xsl:call-template name="toc"/> -->
  
  <xsl:template match="toc" name="toc" mode="jats2html">
    <xsl:param name="toc-max-level" as="xs:integer?"/>
    <xsl:variable name="headlines-by-level" as="element()*">
      <xsl:apply-templates select="$jats2html:toc-headlines[normalize-space()]" mode="toc"/>
    </xsl:variable>
    <xsl:element name="{if($xhtml-version eq '5.0' or $epub-version = 'EPUB3') then 'nav' else 'div'}">
      <xsl:if test="not(self::toc)"><!-- assign id just to generated toc -->
        <xsl:attribute name="id" select="'toc'"/>        
      </xsl:if>
      <xsl:if test="$toc-hidden = ('yes', 'true')"><!-- hide toc -->
        <xsl:attribute name="hidden" select="'hidden'"/>        
      </xsl:if>
      <xsl:attribute name="class" select="'toc'"/>
      <xsl:if test="$xhtml-version eq '5.0'  or $epub-version = 'EPUB3'">
        <xsl:attribute name="epub:type" select="'toc'"/>
      </xsl:if>
      <xsl:choose>
        <xsl:when test="exists(self::toc/* except title-group)">
          <!-- explicitly rendered toc -->
          <xsl:apply-templates mode="jats2html"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:apply-templates select="title-group" mode="jats2html"/>
          <xsl:choose>
            <xsl:when test="$xhtml-version eq '5.0' or $epub-version = 'EPUB3'">
              <xsl:variable name="toc-as-tree">
                <xsl:sequence select="jats2html:flat-toc-to-tree($headlines-by-level, 0, jats2html:set-max-toc-level($toc-max-level, $jats2html:toc-headlines ))"/>
              </xsl:variable>
              <xsl:variable name="patched-toc">
                <xsl:apply-templates select="$toc-as-tree" mode="patch-toc-for-epub3"/>
              </xsl:variable>
              <xsl:sequence select="$patched-toc"/>
            </xsl:when>
            <xsl:otherwise>
              <xsl:sequence select="$headlines-by-level"/>    
            </xsl:otherwise>
          </xsl:choose>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:element>
  </xsl:template>
  
  <xsl:function name="jats2html:set-max-toc-level" as="xs:integer">
    <xsl:param name="toc-max-level" as="xs:integer?"/>
    <xsl:param name="jats2html:toc-headlines" as="element()*"/>
   <xsl:sequence select="($toc-max-level[. castable as xs:integer], 
                                     max(for $i in $jats2html:toc-headlines 
                                         return jats2html:heading-level($i)),
                                     0)[1]"/>
  </xsl:function>
  
  <xsl:template name="page-list">
    <!-- it is better to let epubtools create this list because it will make sure that it is in spine order.
      You need to create <a epub:type="pagebreak" title="IV" id="page-IV"/> out of the target elements for it to work. --> 
    <xsl:if test="//target">
      <xsl:element name="{if($xhtml-version eq '5.0') then 'nav' else 'div'}">
        <xsl:attribute name="id" select="'page-list'"/>
        <xsl:attribute name="epub:type" select="'page-list'"/>
        <xsl:attribute name="aria-label" select="'Page list'"/>
        <ol hidden="">
          <xsl:for-each select="//target">
            <li>
              <a href="#{@id}">
                <xsl:value-of select="."/>
              </a>
            </li>
          </xsl:for-each>
        </ol>
      </xsl:element>
    </xsl:if>
  </xsl:template>
  
  <xsl:template match="html:li[following-sibling::*[1][self::html:ol[not(count(*) eq 1 and html:ol)]]]" mode="patch-toc-for-epub3">
    <xsl:variable name="next-ol" as="element(html:ol)"
                  select="following-sibling::*[1]"/>
    <xsl:copy>
      <xsl:apply-templates select="@*, node()" mode="#current"/>
      <xsl:choose>
        <xsl:when test="$next-ol[count(*) eq 1 and html:ol]">
          <xsl:apply-templates select="$next-ol/@*, $next-ol/html:*" mode="#current"/>
        </xsl:when>
        <xsl:when test="$next-ol">
          <ol>
            <xsl:apply-templates select="$next-ol/@*, $next-ol/html:*" mode="#current"/>
          </ol>  
        </xsl:when>
      </xsl:choose>
    </xsl:copy>
  </xsl:template>
  
  <xsl:template match="html:ol" mode="patch-toc-for-epub3">
    <xsl:choose>
      <xsl:when test="count(*) eq 1 and html:ol">
        <xsl:apply-templates mode="#current"/>
      </xsl:when>
      <xsl:when test="not(preceding-sibling::*[1][self::html:li])">
        <xsl:copy>
         <xsl:apply-templates mode="#current"/>
        </xsl:copy>
      </xsl:when>
    </xsl:choose>
  </xsl:template>
  
  <xsl:template match="html:nav//html:ol/html:ol" mode="clean-up">
    <xsl:apply-templates mode="#current"/>
  </xsl:template>
  
  <xsl:template match="@*|*" mode="patch-toc-for-epub3">
    <xsl:copy>
      <xsl:apply-templates select="@*, node()" mode="#current"/>
    </xsl:copy>
  </xsl:template>
  
  <xsl:function name="jats2html:flat-toc-to-tree" as="element()*">
    <xsl:param name="seq" as="element()*"/>
    <xsl:param name="level" as="xs:integer"/>
    <xsl:param name="max" as="xs:integer"/>
    <xsl:sequence select="tr:flat-list-to-tree($seq, 
                                               $level, 
                                               $max, 
                                               QName('http://www.w3.org/1999/xhtml', 'ol'), 
                                               'class', 
                                               '[a-z]+')"/>
  </xsl:function>
  
  <xsl:template match="title
                      |sec[not(title)]/label
                      |title-group[not(title)]/label" mode="toc">
    <xsl:element name="{if($xhtml-version eq '5.0' or $epub-version = 'EPUB3') then 'li' else 'p'}">
      <xsl:apply-templates select="." mode="toc-class"/>
     
      <a href="#{(@id, generate-id())[1]}" 
         class="toc-link toc-{(parent::title-group/parent::book-part-meta/parent::book-part/@book-part-type,
                               parent::title-group/parent::book-part-meta/parent::*/local-name(),
                               parent::book-part-meta/parent::*/local-name(),
                               parent::index-title-group/parent::index/local-name(),
                               parent::title-group/parent::book-part-meta/parent::*/local-name(),
                               self::sec/local-name(),
                               parent::title-group/parent::*/local-name(),
                               parent::*/local-name()
                               )[1]}">
      <xsl:call-template name="toc-link-content"/>
     </a>
    </xsl:element>
  </xsl:template>
  
  <xsl:template match="title
                      |sec[not(title)]/label
                      |title-group[not(title)]/label" mode="toc-class">
     <xsl:attribute name="class" select="concat('toc', jats2html:heading-level(.))"/>
  </xsl:template>
 
  <xsl:template name="toc-link-content"> 
    <xsl:call-template name="toc-authors"/>
    <xsl:if test="not(self::label) and ../label">
      <span class="toc-label">
        <xsl:apply-templates select="../label/node()" mode="strip-indexterms-etc"/>
        <xsl:value-of select="$subtitle-separator-in-ncx"/>
      </span>
    </xsl:if>
    <xsl:apply-templates mode="jats2html">
      <xsl:with-param name="in-toc" select="true()" as="xs:boolean" tunnel="yes"/>
    </xsl:apply-templates>
  </xsl:template>

  <xsl:template name="toc-authors">
    <!-- you can override this in your adaptations -->
    <xsl:if test="ancestor::book-part-meta/contrib-group/contrib">
      <span class="toc-authors">
        <xsl:value-of select="string-join(for $i in ancestor::book-part-meta/contrib-group/contrib 
                                          return if ($i[string-name[normalize-space()] and not(name)])
                                                 then $i//string-name
                                                 else concat($i//(name[@xml:lang eq $lang], name[1])[1]/given-names, 
                                                                  ' ', 
                                                                  $i//(name[@xml:lang eq $lang], name[1])[1]/surname),
                                            ', ')"/>
       </span>
       <xsl:text>&#x20;</xsl:text>
    </xsl:if>
  </xsl:template>
  
  <xsl:template match="alt-title" mode="jats2html">
    <span class="alt-title" title="{.}"/>
  </xsl:template>
  
  <xsl:template match="toc-entry" mode="jats2html">
    <div class="{local-name()}">
      <xsl:next-match/>
    </div>
  </xsl:template>
  
  <xsl:template match="ext-link" mode="jats2html" priority="3">
    <xsl:param name="in-toc" tunnel="yes" as="xs:boolean?"/>
    <xsl:choose>
      <xsl:when test="$in-toc">
        <xsl:apply-templates mode="#current"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:next-match/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  
  <xsl:template match="target[@id] | inline-graphic" mode="jats2html" priority="2">
    <xsl:param name="in-toc" as="xs:boolean?" tunnel="yes"/>
    <xsl:if test="not($in-toc)">
      <xsl:next-match/>
    </xsl:if>
  </xsl:template>

  <xsl:template match="label[../title union ../caption/title]" mode="jats2html">
    <xsl:param name="actually-process-it" select="true()" as="xs:boolean"/>
    <xsl:if test="$actually-process-it">
      <span class="label">
        <xsl:call-template name="css:content"/>
      </span>
      <xsl:apply-templates select="." mode="label-sep"/>
    </xsl:if>
  </xsl:template>

  <xsl:template match="label[named-content[@content-type = 'post-identifier']]
                            [../title union ../caption/title]" mode="jats2html" priority="3">
    <xsl:param name="actually-process-it" select="true()" as="xs:boolean"/>
    <xsl:if test="$actually-process-it">
      <xsl:apply-templates select="." mode="label-sep"/>
      <span class="label">
        <xsl:call-template name="css:content"/>
      </span>
    </xsl:if>
  </xsl:template>
  
  <xsl:variable name="subtitle-separator-in-ncx" as="xs:string?" select="'&#x2002;'"/>
  <xsl:variable name="author-separator-in-ncx" as="xs:string?" select="': '"/>
  
  <!-- sections where the label is the title, think of capitalized roman numbers in novels -->

  <xsl:template match="sec[not(title)]/label
                      |title-group[not(title)]/label" mode="jats2html" priority="6">
    <xsl:variable name="level" select="jats2html:heading-level(.)" as="xs:integer?"/>
    <xsl:element name="{if ($level) then concat('h', $level) else 'p'}">
      <xsl:call-template name="css:content"/>
    </xsl:element>
  </xsl:template>

  <!-- regular titles -->

  <xsl:template match="title
                      |book-title
                      |article-title[ancestor::title-group]" mode="jats2html">
    <xsl:param name="in-toc" as="xs:boolean?" tunnel="yes"/>
    <xsl:variable name="level" select="jats2html:heading-level(.)" as="xs:integer?"/>
    <xsl:element name="{if ($level) then concat('h', $level) else 'p'}">
      <xsl:copy-of select="(../@id, parent::title-group/../../@id)[1][not($divify-sections = 'yes')]"/>
      <xsl:call-template name="css:other-atts"/>
      <xsl:if test="self::title and ../../.. is /">
        <xsl:message select="'The assertion that this titled element has a grandparent is not correct: ', .."></xsl:message>
      </xsl:if>
      <xsl:sequence select="tr:create-epub-type-attribute(if (self::*:title and ..[self::*:title-group]) then ../../.. else ..)"/>
      <xsl:variable name="_label" as="element(label)?" 
                    select="(../label[not(named-content[@content-type = 'post-identifier'])], 
                             parent::caption/../label[not(named-content[@content-type = 'post-identifier'])]
                             )[1]"/>
      <xsl:variable name="post-label" as="element(label)?" 
                    select="(../label[named-content[@content-type = 'post-identifier']], 
                             parent::caption/../label[named-content[@content-type = 'post-identifier']]
                             )[1]"/>
      <xsl:call-template name="title-att">
        <xsl:with-param name="_label" select="$_label"/>
        <xsl:with-param name="post-label" select="$post-label"/>
      </xsl:call-template>
      <xsl:apply-templates select="$_label" mode="#current">
        <xsl:with-param name="actually-process-it" select="true()" as="xs:boolean"/>
      </xsl:apply-templates>
      <xsl:if test="not($in-toc)">
        <a id="{generate-id()}" />  
      </xsl:if>
      <xsl:call-template name="title-or-alt-title-nodes"/>
      <xsl:apply-templates select="$post-label" mode="#current">
        <xsl:with-param name="actually-process-it" select="true()" as="xs:boolean"/>
      </xsl:apply-templates>
    </xsl:element>
  </xsl:template>
  
  <xsl:template name="title-att">
    <xsl:param name="_label" as="element(label)?"/>
    <xsl:param name="post-label" as="element(label)?"/>
    <xsl:attribute name="title">
      <xsl:if test="$authors-in-titles = 'yes'">
        <xsl:sequence select="jats2html:authors-in-ncx(., root())"/>
      </xsl:if>
      <xsl:apply-templates select="$_label" mode="strip-indexterms-etc"/>
      <xsl:apply-templates select="$_label" mode="label-sep"/>
      <xsl:variable name="stripped" as="text()">
        <xsl:value-of>
          <xsl:apply-templates mode="strip-indexterms-etc"/>
          <xsl:if test="$subtitles-in-titles = 'yes'">
            <xsl:if test="../subtitle[matches(., '\S')]">
              <xsl:value-of select="$subtitle-separator-in-ncx"/>
            </xsl:if>
            <xsl:apply-templates select="../subtitle/node()" mode="strip-indexterms-etc"/>
          </xsl:if>
        </xsl:value-of>
      </xsl:variable>
      <xsl:sequence select="replace($stripped, '^[\p{Zs}\s]*(.+?)[\p{Zs}\s]*$', '$1')"/>
      <xsl:if test="$post-label">
        <xsl:apply-templates select="$post-label" mode="label-sep"/>
        <xsl:apply-templates select="$post-label" mode="strip-indexterms-etc"/>
      </xsl:if>
    </xsl:attribute>
  </xsl:template>
  
  <xsl:template name="title-or-alt-title-nodes">
    <xsl:apply-templates mode="#current"/>
  </xsl:template>
  
  <xsl:function name="jats2html:authors-in-ncx" as="xs:string*">
    <xsl:param name="title" as="element()?"/>
    <xsl:param name="root" as="document-node()"/>
    <xsl:if test="$title[../following-sibling::*[1][self::contrib-group]]">
      <xsl:apply-templates select="$title/../following-sibling::*[1]" mode="strip-indexterms-etc"/>
      <xsl:value-of select="$author-separator-in-ncx"/>
     </xsl:if>
  </xsl:function>
  
  <xsl:template match="index-term | fn | fn/label | target | alt-text |
                       xref[@specific-use=('EndnoteMarker', 'EndnoteRange')][@rid]" mode="strip-indexterms-etc"/>
  
  <xsl:template match="@epub:type[matches(name(..), '^h\d$')]
                                 [../ancestor::*[@epub:type = current()]]" mode="clean-up"/>
  
  <xsl:template match="html:a[@href]
                             [html:span[@class = ('indexterm', 'indexterm-anchor')]]" mode="clean-up">
    <xsl:copy copy-namespaces="no">
      <xsl:apply-templates select="@*" mode="#current"/>
      <xsl:sequence select="node() except html:span[@class = ('indexterm', 'indexterm-anchor')]"/>
    </xsl:copy>
    <xsl:copy-of copy-namespaces="no" 
                 select="html:span[@class = ('indexterm', 'indexterm-anchor')]"/>
  </xsl:template>
  
  <xsl:template match="html:a[html:a[@class eq 'target' or @epub:type eq 'pagebreak']]" mode="clean-up">
    <xsl:variable name="pagebreak" select="html:a[@class eq 'target' or @epub:type eq 'pagebreak']" as="element(html:a)+"/>
    <xsl:copy-of copy-namespaces="no"
                 select="$pagebreak"/>
    <xsl:copy copy-namespaces="no">
      <xsl:apply-templates select="@*" mode="#current"/>
      <xsl:sequence select="node() except $pagebreak"/>
    </xsl:copy>
  </xsl:template>
  
  <!-- Discard certain css markup on titles that would otherwise survive on paras: -->
  <xsl:template match="title/@css:*[matches(local-name(), '^(margin-|text-align)')]" mode="jats2html"/>
  
  <xsl:template match="table-wrap/label" mode="label-sep">
    <xsl:value-of select="$subtitle-separator-in-ncx"/>
  </xsl:template>
  
  <xsl:template match="label" mode="label-sep">
    <xsl:value-of select="$subtitle-separator-in-ncx"/>
  </xsl:template>
  
  <xsl:template match="contrib-group/contrib" mode="jats2html">
    <div class="contrib">
      <xsl:next-match/>
    </div>
  </xsl:template>

  <xsl:template match="string-name" mode="jats2html">
    <span class="{local-name()}">
      <xsl:next-match/>
    </span>
  </xsl:template>
  
  <xsl:template match="p|verse-line" mode="jats2html">
    <p>
      <xsl:next-match/>
    </p>
  </xsl:template>

  <xsl:template match="styled-content" mode="jats2html">
    <span class="{string-join((local-name(), @style, @style-type, @specific-use), ' ')}">
      <xsl:next-match/>
    </span>
  </xsl:template>

  <xsl:template match="styled-content[empty(@* except @srcpath)]" mode="jats2html">
    <xsl:apply-templates mode="#current"/>
  </xsl:template>
  
  <xsl:template match="sup|sub" mode="jats2html">
    <xsl:element name="{name()}">
      <xsl:next-match/>
    </xsl:element>
  </xsl:template>
  
  <xsl:template match="italic" mode="jats2html">
    <i>
      <xsl:next-match/>
    </i>
  </xsl:template>
  
  <xsl:template match="bold" mode="jats2html">
    <b>
      <xsl:next-match/>
    </b>
  </xsl:template>
  
  <xsl:template match="abbrev" mode="jats2html">
    <abbr>
      <xsl:next-match/>
    </abbr>
  </xsl:template>
  
  <xsl:template match="abbrev/def" mode="jats2html">
    <span class="def">
      <xsl:apply-templates select="p/node()" mode="#current"/>
    </span>
  </xsl:template>
  
  <xsl:template match="underline" mode="hub2htm:css-style-overrides">
    <xsl:attribute name="css:text-decoration" select="'underline'"/>
  </xsl:template>
  
  <xsl:template match="monospace" mode="hub2htm:css-style-overrides">
    <xsl:attribute name="css:font-family" select="'monospace'"/>
  </xsl:template>
  
  <xsl:template match="sc" mode="hub2htm:css-style-overrides">
    <xsl:attribute name="css:font-variant" select="'small-caps'"/>
  </xsl:template>
  
  <xsl:template match="strike" mode="hub2htm:css-style-overrides">
    <xsl:attribute name="css:text-decoration" select="'line-through'"/>
  </xsl:template>
  
  <xsl:template match="overline" mode="hub2htm:css-style-overrides">
    <xsl:attribute name="css:text-decoration" select="'overline'"/>
  </xsl:template>
  
  <xsl:template match="sans-serif" mode="hub2htm:css-style-overrides">
    <xsl:attribute name="css:font-family" select="'sans-serif'"/>
  </xsl:template>
  
  <xsl:template match="roman" mode="hub2htm:css-style-overrides">
    <xsl:attribute name="css:font-family" select="'serif'"/>
  </xsl:template>
  
  <xsl:template match="ref" mode="jats2html" priority="8">
    <p class="{name()}">
      <xsl:next-match/>
    </p>
  </xsl:template>

  <xsl:template match="ref[@id]/*[last()][$bib-backlink-type = 'letter']" mode="jats2html" priority="2">
    <xsl:next-match/>
    <xsl:value-of select="$subtitle-separator-in-ncx"/>
    <xsl:for-each select="key('by-rid', parent::ref/@id)">
      <a href="#xref_{@id}" id="{generate-id()}" class="ref-link">
        <xsl:choose>
          <xsl:when test="position() eq 1 and position() eq last()">
            <xsl:text>→</xsl:text>
          </xsl:when>
          <xsl:otherwise>
            <xsl:number format="a" value="position()"/>    
          </xsl:otherwise>
        </xsl:choose>
      </a>
      <xsl:if test="position() ne last()">
        <xsl:text xml:space="preserve">, </xsl:text>
      </xsl:if>
    </xsl:for-each>
  </xsl:template>
  
  <xsl:variable name="ref-index" select="ref-list/ref" as="element(ref)*"/>
  
  <xsl:template match="ref" mode="jats2html" priority="1.5">
    <xsl:if test="tr:create-epub-type-attribute(.)">
      <xsl:attribute name="epub:type" select="tr:create-epub-type-attribute(.)"/>
    </xsl:if>
    <xsl:apply-templates select="@*" mode="#current"/>
    <xsl:if test="not(label) and $number-bibliography eq 'yes'">
      <xsl:variable name="id" select="@id" as="attribute(id)?"/>
      <span class="ref-number">
        <xsl:value-of select="(//xref[@rid eq $id][string-length(.) gt 0], index-of($ref-index, .))[1]"/>
      </span>
    </xsl:if>
    <xsl:apply-templates select="label, (mixed-citation, element-citation, citation-alternatives)[1], note, x" mode="#current"/>
  </xsl:template>

  <!-- Most of these matching elements need to be synced with the next-match css:content template
    approx. 1400 lines above. -->
  <xsl:template match="addr-line
                      |address
                      |article-title
                      |chapter-title
                      |conf-loc
                      |conf-name
                      |city
                      |collab
                      |comment
                      |country
                      |date
                      |date-in-citation
                      |day
                      |degrees
                      |edition
                      |elocation-id
                      |equation-count
                      |etal
                      |fig-count
                      |fpage
                      |given-names
                      |gov
                      |hr
                      |institution
                      |institution-wrap
                      |issue
                      |issue-id
                      |issue-part
                      |issue-title
                      |kwd
                      |label
                      |lpage
                      |monospace
                      |month
                      |named-content
                      |nested-kwd
                      |overline
                      |page-range
                      |person-group
                      |postal-code
                      |prefix
                      |private-char
                      |pub-id
                      |publisher-loc
                      |publisher-name
                      |role
                      |roman
                      |sans-serif
                      |sc
                      |season
                      |series
                      |size
                      |source
                      |state
                      |std
                      |strike
                      |string-date
                      |subject
                      |suffix
                      |supplement
                      |surname
                      |table-count
                      |trans-source
                      |trans-subtitle
                      |trans-title
                      |trans-title-group
                      |underline
                      |uri[not(@xlink:href)]
                      |volume
                      |volume-id
                      |volume-series
                      |year
                      |x" mode="jats2html"> 
    <span class="{local-name()}">
      <xsl:next-match/>
    </span> 
  </xsl:template>

  <xsl:template match="@person-group-type" mode="jats2html"/>

  <!--  *
        * index 
        * -->

  <!--  BITS can contain two ways markup an index:
        (1) There are index-terms embedded in the main body and we generate an index from these.
        (2) A list of index-entry elements already exists which is not linked. Most likely, you
            would just take these with their given order. -->
  
  <xsl:variable name="jats:index-symbol-heading"   as="xs:string"  select="$index-symbol-heading"/>
  <xsl:variable name="jats:index-generate-title"   as="xs:string"  select="$index-generate-title"/>
  <xsl:variable name="jats:index-fallback-title"   as="xs:string"  select="$index-fallback-title"/>
  <xsl:variable name="jats:index-heading-elt-name" as="xs:string"  select="$index-heading-elt-name"/>
  <xsl:variable name="jats:index-heading-class"    as="xs:string"  select="$index-heading-class"/>
  
  <!-- create index sections and generate titles first. in jats2html the 
       sections will be poulated and the index section is inserted into the toc -->
  
  <xsl:template match="book" mode="epub-alternatives">
    <xsl:variable name="available-index-types" as="xs:string*"
                  select="distinct-values(for $i in //index-term
                                          return ($i/@index-type, 'index')[1])"/>
    <xsl:variable name="existing-indexes" as="xs:string+"
                  select="if(//index/@index-type) then //index/@index-type else 'index'"/>
    <xsl:copy>
      <xsl:apply-templates select="@*, node()" mode="#current"/>
      <xsl:for-each select="$available-index-types[not(. = $existing-indexes)]">
        <xsl:variable name="index-type" select="." as="xs:string"/>
        <index xmlns="" index-type="{$index-type}">
          <index-title-group>
            <title>
              <xsl:value-of select="(concat(upper-case(substring($index-type, 1, 1)), substring($index-type, 2)),
                                     $jats:index-fallback-title)[1]"/>
            </title>
          </index-title-group>
        </index>
      </xsl:for-each>
    </xsl:copy>
  </xsl:template>
  
  <!-- this template either renders an existing index 
       or is invoked with call-template to create a new index -->
  
  <xsl:template match="index" name="create-index" mode="jats2html">
    <xsl:param name="context" select="."              as="element()?"/>
    <xsl:param name="root" select="/"                 as="document-node()"/>
    <xsl:param name="index-type" select="@index-type" as="xs:string?"/>
    <xsl:element name="{$default-container-name}">
      <xsl:variable name="index-type" select="$index-type" as="xs:string?"/>
      <xsl:attribute name="class" select="string-join(('index', $index-type), ' ')"/>
      <xsl:attribute name="epub:type" select="'index'"/>
      <xsl:if test="$context">
        <xsl:apply-templates select="$context/@*" mode="#current"/>  
      </xsl:if>
      <!-- if a rendered index exists, we don't generate a new one from index-terms -->
      <xsl:choose>
        <xsl:when test="$context//index-entry">
          <xsl:call-template name="group-index-entries">
            <xsl:with-param name="level" select="1"/>
          </xsl:call-template>
        </xsl:when>
        <xsl:otherwise>
          <xsl:apply-templates select="$context/index-title-group" mode="#current"/>  
          <xsl:for-each-group select="$root//index-term[not(ancestor::index-term)]
                                                       [if(@index-type) then @index-type eq $index-type else true()]"
                              group-by="if (matches(substring(jats2html:strip-combining((@sort-key, term)[1]), 1, 1), 
                                                    '[A-z\p{IsLatin-1Supplement}]')) 
                                        then substring(jats2html:strip-combining((@sort-key, term)[1]), 1, 1) 
                                        else '0'"
                              collation="http://saxon.sf.net/collation?lang={($root/*/@xml:lang, 'de')[1]};strength=primary">
            <xsl:sort select="current-grouping-key()" 
                      collation="http://saxon.sf.net/collation?lang={($root/*/@xml:lang, 'de')[1]};strength=primary"/>
            <xsl:element name="{$jats:index-heading-elt-name}">
              <xsl:attribute name="class" select="$jats:index-heading-class"/>
              <xsl:value-of select="if (matches(current-grouping-key(), '[A-z\p{IsLatin-1Supplement}]') and current-grouping-key() ne '0') 
                                    then upper-case(current-grouping-key()) 
                                    else $jats:index-symbol-heading"/>
            </xsl:element>
            <xsl:call-template name="group-index-terms">
              <xsl:with-param name="level" select="1"/>
              <xsl:with-param name="index-terms" select="current-group()"/>
            </xsl:call-template>
          </xsl:for-each-group>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:element>
  </xsl:template>
  
  <xsl:template match="index-title-group" name="create-index-title-group" mode="jats2html">
    <xsl:param name="context" select="." as="element(index-title-group)"/>
    <xsl:apply-templates select="$context/title" mode="#current"/>
  </xsl:template>
  
  <xsl:template name="group-index-entries">
    <xsl:param name="level" as="xs:integer"/>
    <xsl:for-each-group select="*" group-adjacent="local-name()">
      <xsl:choose>
        <xsl:when test="current-grouping-key() eq 'index-title-group'">
          <xsl:apply-templates select="current-group()" mode="#current"/>
        </xsl:when>
        <xsl:when test="current-grouping-key() eq 'index-div'">
          <xsl:for-each select="current-group()">
            <ul class="index-entry-list" epub:type="index-entry-list">
              <li>
                <xsl:call-template name="group-index-entries">
                  <xsl:with-param name="level" select="$level"/>
                </xsl:call-template>
              </li>
            </ul>
          </xsl:for-each>
        </xsl:when>
        <xsl:when test="current-grouping-key() eq 'index-entry'">
          <ul class="index-entry-list" epub:type="index-entry-list">
            <xsl:for-each select="current-group()">
              <li class="ie ie{$level}" epub:type="index-entry">
                <xsl:apply-templates select="* except (index-entry|nav-pointer|nav-pointer-group)" mode="index-term"/>                
                <xsl:for-each select="nav-pointer[@rid] union nav-pointer-group/nav-pointer[@rid]">
                  <xsl:if test="position() = 1">
                    <xsl:text>&#x20;</xsl:text>
                  </xsl:if>
                  <xsl:if test="current()/@nav-pointer-type='end-of-range'">
                    <xsl:text>-</xsl:text>
                  </xsl:if>
                  <xsl:apply-templates select="." mode="index-term"/>
                  <xsl:if test="position() ne last() and not(current()/@nav-pointer-type='start-of-range')">
                    <xsl:text>,&#x20;</xsl:text>
                  </xsl:if>
                </xsl:for-each>
                <xsl:if test="index-entry">
                  <!-- recurse into sub index entries -->
                  <xsl:call-template name="group-index-entries">
                    <xsl:with-param name="level" select="$level + 1" as="xs:integer"/>
                  </xsl:call-template>
                </xsl:if>
              </li>
            </xsl:for-each>
          </ul>
        </xsl:when>
        <xsl:when test="self::nav-pointer-group">
          <xsl:apply-templates select="." mode="index-term"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:apply-templates select=".[not(self::term
                                            |self::see-also
                                            |self::see-entry
                                            |self::see-also-entry
                                            |self::x)]" mode="jats2html"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:for-each-group>
  </xsl:template>
  
  <xsl:template match="term" mode="index-term">
    <span class="indexterm" epub:type="index-term">
      <xsl:apply-templates select="node() except index-term" mode="jats2html"/>
    </span>
  </xsl:template>
  
  <xsl:template match="nav-pointer[@rid]" mode="index-term">
    <a class="{local-name()}" href="#{@rid}">
      <xsl:apply-templates mode="jats2html"/>
    </a>
  </xsl:template>
  
  <xsl:template match="nav-pointer-group|see-entry|see-also-entry" mode="index-term">
    <span class="{local-name()}">
      <xsl:apply-templates mode="#current"/>
    </span>
  </xsl:template>
  
  <xsl:template match="x" mode="index-term">
    <xsl:apply-templates mode="jats2html"/>
    <xsl:text>&#x20;</xsl:text>
  </xsl:template>
  
  <xsl:template name="group-index-terms">
    <xsl:param name="level" as="xs:integer"/>
    <xsl:param name="index-terms" as="element(index-term)*"/>
    <!-- §§§ We need to know a book’s main language! -->
    <xsl:if test="count($index-terms) gt 0">
      <ul class="index-entry-list" epub:type="index-entry-list">
        <xsl:for-each-group select="$index-terms" 
                            group-by="(@sort-key, term)[1]"
                            collation="http://saxon.sf.net/collation?lang={(/*/@xml:lang, 'de')[1]};strength=identical">
          <xsl:sort select="current-grouping-key()" collation="http://saxon.sf.net/collation?lang={(/*/@xml:lang, 'de')[1]};strength=primary"/>
          <xsl:sort select="current-grouping-key()" collation="http://saxon.sf.net/collation?lang={(/*/@xml:lang, 'de')[1]};strength=identical"/>
          <xsl:call-template name="index-entry">
            <xsl:with-param name="level" select="$level"/>
          </xsl:call-template>
        </xsl:for-each-group>
      </ul>  
    </xsl:if>
  </xsl:template>
  
  <xsl:template name="index-entry">
    <xsl:param name="level" as="xs:integer"/>
    <xsl:variable name="cg" select="current-group()"/>
    <li class="ie ie{$level}" epub:type="index-entry">
      <xsl:apply-templates select="current-group()[1]/term" mode="index-term"/>
      <xsl:value-of select="$subtitle-separator-in-ncx"/>
      <xsl:for-each select="current-group()[exists(index-term)
                                            or
                                            jats2html:contains-token(@content-type, 'hub:not-placed-on-page')]">
        <a id="ie_{@id}"/>
      </xsl:for-each>
      <xsl:for-each select="current-group()[empty(index-term)]
                                           [not(some $a in ancestor-or-self::*[self::index-term]/@content-type satisfies jats2html:contains-token($a, 'hub:not-placed-on-page'))]">
       <xsl:variable name="style" select="if (current-group()[1]/ancestor-or-self::index-term[last()]/@content-type[matches(., '^(hub:page-num-)?(bold|italic|bolditalic)$')]) 
                                          then  replace(current-group()[1]/ancestor-or-self::index-term[last()]/@content-type, '^(hub:page-num-)?(bold|italic|bolditalic)$', '$2')
                                          else ()" as="xs:string?"/>
        <a href="#it_{@id}" id="ie_{@id}" epub:type="index-locator">
          <xsl:attribute name="class" select="string-join(('index-link', $style)[normalize-space()], ' ')"/>
          <xsl:value-of select="position()"/>
        </a>
        <xsl:if test="position() ne last()(: or (current-group()[see] and position() = last()):)">
          <xsl:text xml:space="preserve">, </xsl:text>
        </xsl:if>
      </xsl:for-each>
      <xsl:for-each-group select="current-group()/see" group-by="string(.)">
        <xsl:if test="position() = 1 and not(matches(.,'siehe','i'))">
          <xsl:value-of select="if ($root/*/@xml:lang = 'de') 
                                then 
                                  if ($cg[jats2html:contains-token(@content-type, 'hub:not-placed-on-page')])
                                  then 'siehe ' 
                                  else ' siehe ' 
                                else ' see '" xml:space="preserve"/>
        </xsl:if>
        <xsl:if test="position() = 1 ">
          <xsl:value-of select="' '" xml:space="preserve"/>
        </xsl:if>
        <xsl:call-template name="potentially-link-to-see-target"/>
        <xsl:if test="not(position() = last())">
          <xsl:text>; </xsl:text>
        </xsl:if>
      </xsl:for-each-group>
      <xsl:if test="current-group()//see and current-group()//see-also">
        <xsl:text xml:space="preserve">;</xsl:text>
      </xsl:if>
      <xsl:for-each-group select="current-group()/see-also" group-by="string(.)">
        <xsl:value-of select="if($root/*/@xml:lang = 'de') 
                              then 
                                  if ($cg[jats2html:contains-token(@content-type, 'hub:not-placed-on-page')]
                                      and 
                                      not(preceding-sibling::*[1][self::see-also | self::see]))
                                  then 'siehe auch ' 
                                  else ' siehe auch ' 
                                else ' see also '" xml:space="preserve"/>
        <xsl:call-template name="potentially-link-to-see-target"/>
        <xsl:if test="not(position() = last())">
          <xsl:text>;</xsl:text>
        </xsl:if>
      </xsl:for-each-group>
      <xsl:call-template name="group-index-terms">
        <xsl:with-param name="index-terms" select="current-group()/index-term"/>
        <xsl:with-param name="level" select="$level + 1"/>
      </xsl:call-template>
    </li>
  </xsl:template>
  
  <xsl:key name="jats2html:by-indext-term" 
           match="index-term" use="term, string-join((parent::index-term/term, term), ', ')"/>
  
  <xsl:template name="potentially-link-to-see-target">
    <xsl:param name="root" as="document-node()" tunnel="yes"/>
    <!-- Context: see or see-also -->
    <xsl:variable name="target" as="element(index-term)?"
      select="(key('by-id', @rid, $root)/self::index-term,
               key('jats2html:by-indext-term', concat(., ' (', ../term, ')'), $root),
               key('jats2html:by-indext-term', ., $root))[1]"/>
    <xsl:choose>
      <xsl:when test="exists($target)">
        <a href="#ie_{$target/@id}">
          <xsl:value-of select="."/>
        </a>
      </xsl:when>
      <xsl:otherwise>
        <xsl:apply-templates mode="#current"/>
      </xsl:otherwise>
    </xsl:choose>

  </xsl:template>

  <xsl:template match="index-term" mode="jats2html">
    <xsl:param name="in-toc" as="xs:boolean?" tunnel="yes"/>
    <xsl:if test="not($in-toc)">
      <span class="indexterm-anchor" id="it_{(descendant-or-self::index-term[last()]/@id, generate-id())[1]}">
        <xsl:attribute name="title">  
          <xsl:apply-templates mode="#current"/>
        </xsl:attribute>
        <xsl:if test="$index-backlink-type = ('text-and-number', 'number')">
          <a href="#ie_{descendant-or-self::index-term[last()]/@id}" class="it">
            <span class="it"/>
            <xsl:if test="$index-backlink-type = ('text-and-number')">
              <xsl:text xml:space="preserve"> </xsl:text>
              <xsl:apply-templates mode="#current"/>
            </xsl:if>
          </a>
        </xsl:if>
      </span>
    </xsl:if>
    <xsl:apply-templates select="term/index-term" mode="#current"/>
  </xsl:template>

  <!-- <index-term-range-end> is a marker to specify the range of an index-term.
       Its @rid must match the @id of a previous <index-term>. -->
  
  <xsl:template match="index-term-range-end" mode="jats2html">
    <a class="{local-name()}" id="{@rid}"/>
  </xsl:template>
  
  <!-- for index terms -->
  <xsl:template match="html:span[@class eq 'it']" mode="clean-up">
    <xsl:copy copy-namespaces="no">
      <xsl:apply-templates select="@*" mode="#current"/>
      <xsl:text>(</xsl:text>
      <xsl:value-of select="key('by-id', substring-after(../@href, '#'))"/>
      <xsl:text>)</xsl:text>
    </xsl:copy>
  </xsl:template>
  
  <!-- ADE EPUB reader doesn't display background colors for 
       rows. So we copy them from row to cell unless the cell 
       contains any other background styles. -->
  
  <xsl:template match="*[local-name() = ('th', 'td')]
                        [not(key('rule-by-name', @content-type)/@css:background-color or @css:background-color)]
                        [parent::tr[@css:background-color]]" mode="epub-alternatives">
    <xsl:copy>
      <xsl:apply-templates select="@* except @css:background-color" mode="#current"/>
      <xsl:attribute name="css:background-color" select="parent::tr/@css:background-color"/>
      <xsl:apply-templates mode="#current"/>
    </xsl:copy>
  </xsl:template>
  
  <xsl:template match="@style" mode="jats2html">
    <xsl:copy-of select="."/>
  </xsl:template>
  
  <xsl:template match="tr/@css:background-color" mode="epub-alternatives"/>

  <xsl:template match="index-term/term" mode="jats2html">
    <xsl:apply-templates mode="#current"/>
  </xsl:template>

  <xsl:template match="index-term[parent::index-term]" mode="jats2html">
    <xsl:text xml:space="preserve">, </xsl:text>
    <xsl:apply-templates mode="#current"/>
  </xsl:template>
  
  <xsl:template match="see" mode="jats2html">
    <xsl:if test="not(matches(string-join(descendant::text(),''),'siehe|see','i'))">
      <xsl:value-of select="if($root/*/@xml:lang = 'de') then ' siehe ' else ' see '" xml:space="preserve"/>
    </xsl:if>
    <xsl:apply-templates mode="#current"/>
  </xsl:template>
  
  <xsl:template match="see-also" mode="jats2html">
    <xsl:if test="not(matches(string-join(descendant::text(),''),'siehe auch|see also','i'))">
      <xsl:value-of select="if($root/*/@xml:lang = 'de') then ' siehe auch ' else ' see also '" xml:space="preserve"/>
    </xsl:if>
    <xsl:apply-templates mode="#current"/>
  </xsl:template>
  
  <xsl:variable name="block-element-names" as="xs:string+" 
                select="'answer',
                        'array',
                        'book-title',
                        'boxed-text',
                        'code',
                        'def-list',
                        'disp-formula',
                        'disp-formula-group',
                        'disp-quote',
                        'explanation',
                        'fig',
                        'fig-group',
                        'list',
                        'p',
                        'preformat',
                        'question',
                        'table-wrap',
                        'speech',
                        'statement',
                        'verse-group'"/>

  <xsl:template match="p[*[local-name() = $block-element-names]]" mode="jats2html" priority="1.2">
    <xsl:for-each-group select="node()" 
                        group-adjacent="boolean(self::*[local-name() = $block-element-names])">
      <xsl:choose>
        <xsl:when test="current-grouping-key()">
          <xsl:apply-templates select="current-group()" mode="#current"/>
        </xsl:when>
        <xsl:when test="every $item in current-group() 
                        satisfies ($item/self::text()[not(normalize-space())])"/>
        <xsl:otherwise>
          <xsl:element name="{name(..)}">
            <xsl:for-each select="..">
              <xsl:call-template name="css:other-atts"/>
            </xsl:for-each>
            <xsl:apply-templates select="current-group()" mode="#current"/>
          </xsl:element>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:for-each-group>
  </xsl:template>
  
  <xsl:template match="boxed-text" mode="jats2html">
    <xsl:element name="{if($xhtml-version eq '5.0' and @position = ('margin', 'float')) 
                        then 'aside' 
                        else 'div'}">
      <xsl:attribute name="class" 
                     select="string-join(('box', 
                                          @content-type, 
                                          @position,
                                          if(alternatives) then 'alt-image' else ()), ' ')"/>
      <xsl:apply-templates select="@* except @content-type, label" mode="#current"/>
      <div class="box-content">
        <xsl:apply-templates select="if(alternatives) 
                                     then alternatives 
                                     else *[not(self::label)]" mode="#current"/>
      </div>
    </xsl:element>
  </xsl:template>
  
  <!-- graphics -->
  
  <xsl:template match="graphic | inline-graphic" mode="jats2html">
    <img>
      <xsl:call-template name="jats2html:img-alt"/>
      <xsl:apply-templates select="@srcpath, @xlink:href" mode="#current"/>
      <xsl:apply-templates select="." mode="class-att"/>
    </img>
    <xsl:apply-templates select="* except alt-text" mode="#current"/>
  </xsl:template>
  
  <xsl:template name="jats2html:img-alt">
    <xsl:variable name="graphic-in-fig-pos" as="xs:integer"
                  select="(index-of(parent::fig/graphic/generate-id(), generate-id()), 1)[1]"/>
    <xsl:attribute name="alt" select="(alt-text, parent::fig/alt-text[$graphic-in-fig-pos], @xlink:title)[1]"/>
  </xsl:template>
  
  <xsl:template match="graphic[caption and not(parent::fig)][$xhtml-version eq '5.0']" mode="jats2html" priority="5">
    <figure class="{local-name()}">
      <xsl:next-match/>
    </figure>
  </xsl:template>
  
  <xsl:template match="alt-text" mode="jats2html"/>

  <xsl:template match="*[local-name() = ('graphic', 'inline-graphic')]/@xlink:href" mode="jats2html">
    <xsl:attribute name="src" select="."/>
  </xsl:template>

  <xsl:template match="graphic/@css:*" mode="jats2html"/>

  <xsl:template match="*[local-name() = ('graphic', 'inline-graphic')]/@*[name() = ('css:width', 'css:height')]"
    mode="hub2htm:css-style-overrides"/>

  <xsl:template match="graphic/attrib" mode="jats2html"/>
  
  <!-- media -->
  
  <xsl:template match="media" mode="jats2html">
    <xsl:variable name="media-type" as="xs:string"
                  select="if(matches(@mimetype, '^audio')) then 'audio' else 'video'" />
    <xsl:element name="{$media-type}">
      <xsl:attribute name="controls" select="'controls'"/>
      <source src="{@xlink:href}" type="{@mimetype}"/>
      <xsl:apply-templates select="alt-text, long-desc" mode="#current"/>
      <xsl:value-of select="concat('Your browser or device does not support ', $media-type)"/>
    </xsl:element>
  </xsl:template>
  
  <xsl:template match="object-id" mode="jats2html">
    <a class="{string-join((local-name(), 
                            for $i in @*[not(local-name() = 'id')] 
                            return concat($i/local-name(), '__', $i)
                            ), ' ')}" 
       title="{normalize-space(.)}">
      <xsl:apply-templates select="@id" mode="#current"/>
    </a>
  </xsl:template>
  
  <!-- formulas -->
  
  <xsl:template match="disp-formula-group|disp-formula" mode="jats2html">
    <div class="{local-name()}">
      <xsl:next-match/>
    </div>
  </xsl:template>
  
  <xsl:template match="inline-formula" mode="jats2html">
    <span class="{name()}">
      <xsl:apply-templates select="@srcpath, node()" mode="#current"/>
    </span>
  </xsl:template>
  
  <xsl:template match="alternatives" mode="jats2html">
    <span class="{local-name()}">
      <xsl:apply-templates select="@*, (mml:math, tex-math, media, (graphic|inline-graphic), *)[1]" mode="#current"/>  
    </span>
  </xsl:template>
  
  <xsl:template match="mml:math" mode="jats2html">
    <xsl:variable name="altimg" as="attribute(xlink:href)?"
                  select="parent::alternatives/*[local-name() = ('graphic', 'inline-graphic')][1]/@xlink:href"/>
    <xsl:element name="{local-name()}" namespace="http://www.w3.org/1998/Math/MathML">
      <!-- Unlike HTML, EPUB 3.0 requires an alttext attribute. -->
      <xsl:attribute name="alttext">
        <xsl:if test="tr:unwrap-mml-boolean(.)">
          <xsl:apply-templates mode="unwrap-mml"/>
        </xsl:if>
      </xsl:attribute>
      <xsl:if test="$altimg">
        <xsl:attribute name="altimg" select="$altimg"/>
      </xsl:if>
      <xsl:apply-templates select="@*, node()" mode="#current"/>
    </xsl:element>
  </xsl:template>
  
  <!-- strip ns prefix, mathjax and some browsers have issues with xml namespaces -->
  
  <xsl:template match="mml:*" mode="jats2html">
    <xsl:element name="{local-name()}" namespace="http://www.w3.org/1998/Math/MathML">
      <xsl:copy-of select="@*"/>
      <xsl:apply-templates mode="#current"/>
    </xsl:element>
  </xsl:template>
  
  <xsl:template match="table-wrap/alternatives[graphic]
                      |boxed-text/alternatives[graphic]" mode="jats2html" priority="2">
    <xsl:for-each select="graphic">
      <img>
        <xsl:attribute name="class" select="local-name()"/>
        <xsl:attribute name="src" select="@xlink:href"/>
        <xsl:attribute name="alt" select="concat('Alternative image for table ', @xlink:href)"/>
        <xsl:apply-templates select="@srcpath" mode="#current"/>
      </img>
    </xsl:for-each>
  </xsl:template>
  
  <xsl:template match="tex-math" mode="jats2html">
    <xsl:element name="{if(ancestor::disp-formula) then 'div' else 'span'}">
      <xsl:attribute name="class" select="local-name()"/>
      <xsl:apply-templates select="@srcpath" mode="#current"/>
    </xsl:element>
  </xsl:template>
  
  <!-- tables -->
  
  <!-- map xhtml 1.0/1.1 table model to xhtml 5.0 -->
  
  <xsl:template match="table[col[@* except @srcpath]][$xhtml-version eq '5.0']" mode="jats2html" priority="5">
    <table>
      <xsl:apply-templates select="@*, caption" mode="#current"/>
      <colgroup>
        <xsl:apply-templates select="col" mode="#current"/>
      </colgroup>
      <xsl:apply-templates select="* except (caption|col)" mode="#current"/>
    </table>
  </xsl:template>
  
  <xsl:template match="colgroup[every $i in col satisfies $i/not(@* except @srcpath)][$xhtml-version eq '5.0']
                      |col[every $i in parent::*/col satisfies $i/not(@* except @srcpath)][$xhtml-version eq '5.0']" 
                mode="jats2html"/>
  
  <xsl:template match="col[@align
                          |@bgcolor
                          |@width
                          |@valign][$xhtml-version eq '5.0']" mode="jats2html">
    <col>
      <xsl:apply-templates select="@span, @srcpath" mode="#current"/>
      <xsl:attribute name="style"
                     select="string-join((@style,
                                          @align/concat('text-align:', .),
                                          @bgcolor/concat('background-color:', .),
                                          @width/concat('width:', .),
                                          @valign/concat('vertical-align:', .)
                                          ), 
                                         '; ')"/>
    </col>
  </xsl:template>
  
  <xsl:template match="tr 
                      |tbody
                      |thead
                      |tfoot
                      |td
                      |th
                      |colgroup
                      |col
                      |table[not(matches(@css:width, 'pt$'))]" mode="jats2html">
    <xsl:element name="{local-name()}" exclude-result-prefixes="#all">
      <xsl:call-template name="css:content"/>
    </xsl:element>
  </xsl:template>
  
  <xsl:template match="array" mode="jats2html">
    <xsl:variable name="caption" as="element()?">
      <xsl:if test="label">
        <div class="array-caption caption">
          <p>
            <xsl:apply-templates select="label/node()" mode="#current"/>
          </p>
        </div>
      </xsl:if>
    </xsl:variable>
    <div class="{local-name()}">
      <xsl:sequence select="$caption"/>
      <table class="{local-name()}">
        <xsl:call-template name="css:content"/>
      </table>  
    </div>
  </xsl:template>
  
  <xsl:template match="array/label" mode="jats2html"/>

  <xsl:template match="*[name() = ('table', 'array')][matches(@css:width, 'pt$')]" mode="jats2html">
    <xsl:param name="root" as="document-node()?" tunnel="yes"/>
    <xsl:param name="table-widths-created" as="xs:boolean?" tunnel="yes" select="false()"/>
    
    <xsl:choose>
      <xsl:when test="$table-widths-created">
        <!-- if jats2html:table-width-grid() returns 0, widths were preserved and stylesheet could loop.-->
         <xsl:element name="{name()}">
           <xsl:call-template name="css:content"/>
         </xsl:element>
      </xsl:when>
      <xsl:otherwise>
        <xsl:variable name="conditional-percent-widths" as="element(*)">
          <xsl:apply-templates select="." mode="table-widths"/>
        </xsl:variable>
        <xsl:apply-templates select="$conditional-percent-widths" mode="#current">
          <xsl:with-param name="root" select="($root, root(.))[1]" as="document-node()" tunnel="yes"/>
          <xsl:with-param name="table-widths-created" select="true()" as="xs:boolean" tunnel="yes"/>
        </xsl:apply-templates>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  
  <!-- There should always be @css:width. @width is only decorational (will be valuable just in case 
    all @css:* will be stripped -->
  <xsl:template match="@width[not($epub-version = 'EPUB2')]" mode="jats2html"/>
  
  <xsl:template match="table//@width[$epub-version = 'EPUB2']" mode="jats2html">
    <xsl:copy-of select="."/>
  </xsl:template>

  <xsl:template match="*[name() = ('table', 'array')][@css:width]" mode="table-widths">
    <xsl:variable name="twips" select="tr:length-to-unitless-twip(@css:width)" as="xs:double?"/>
    <!--  <xsl:message select="'###', string-join(caption, ''), ' p-w-t: ', $page-width-twips, ' twips: ', $twips "/>-->
    <xsl:choose>
      <xsl:when test="$twips">
        <table xmlns="">
          <xsl:if test="local-name() eq 'array'">
            <xsl:attribute name="class" select="'array'"/>
          </xsl:if>
          <xsl:apply-templates select="@*, node()" mode="#current">
            <xsl:with-param name="table-twips" select="$twips" tunnel="yes"/>
            <xsl:with-param name="table-percentage" select="jats2html:table-width-grid($page-width-twips, $twips)" tunnel="yes"/>
          </xsl:apply-templates>
        </table>
      </xsl:when>
      <xsl:otherwise>
        <xsl:next-match/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>  
  
  <xsl:template match="*[name() = ('table', 'array')]/@css:width" mode="table-widths">
    <xsl:param name="table-twips" as="xs:double?" tunnel="yes"/>
    <xsl:param name="table-percentage" as="xs:integer?" tunnel="yes"/>
    <xsl:choose>
      <xsl:when test="not($table-twips) or not($table-percentage)">
        <xsl:copy/>
      </xsl:when>
      <xsl:when test="$table-percentage eq 0">
        <xsl:copy/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:choose>
          <xsl:when test="not($epub-version = 'EPUB2')">
            <xsl:attribute name="css:width" select="concat($table-percentage, '%')"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:attribute name="width" select="concat($table-percentage, '%')"/>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="  *[name() = ('table', 'array')][not(col | colgroup)][@css:width]/*/tr/*/@css:width
                       | *[name() = ('table', 'array')][exists(col | colgroup)][@css:width]//col/@width
                       | *[name() = ('table', 'array')][exists(col | colgroup)]/*
                            /tr[position() = 1]
                               [$copy-colwidths = 'yes']/*/@css:width" 
                mode="table-widths">
    <!-- retain cell widths in the first rows because neither ADE nor Bluefire seem to honor widths in colgroup/col,
         https://redmine.le-tex.de/issues/8516 -->
    <xsl:param name="table-twips" as="xs:double?" tunnel="yes"/>
    <xsl:param name="table-percentage" as="xs:integer?" tunnel="yes"/>
    <xsl:variable name="att" as="attribute(css:width)">
      <xsl:choose>
        <xsl:when test="not($table-twips) or not($table-percentage)">
          <xsl:attribute name="css:width" select="."/>
        </xsl:when>
        <xsl:when test="$table-percentage eq 0">
          <xsl:attribute name="css:width" select="."/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:attribute name="css:width" 
            select="concat(string(xs:integer(1000 * (tr:length-to-unitless-twip(.) div $table-twips)) * 0.1), '%')"/>    
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:choose>
      <xsl:when test="not($epub-version = 'EPUB2')">
        <xsl:sequence select="$att"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:attribute name="width" select="$att"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="*[name() = ('table', 'array')]
                        [exists(col | colgroup)]/*
                          /tr[position() gt (if ($copy-colwidths = 'yes') then 1 else 0)]/*/@css:width"
    mode="table-widths">
    <!-- retain cell widths in the first rows because neither ADE nor Bluefire seem to honor widths in colgroup/col,
         https://redmine.le-tex.de/issues/8516 -->
  </xsl:template>

  <!-- will be discarded -->
  <xsl:variable name="jats2html:masterpageobjects-para-regex" select="'tr_(pagenumber|columntitle)'" as="xs:string"/>
  
  <xsl:template match="*[matches(@role, $jats2html:masterpageobjects-para-regex)]" mode="jats2html"/>

  <xsl:template match="@colspan | @rowspan" mode="jats2html">
    <xsl:copy/>
  </xsl:template>
  
  <xsl:template match="ext-link|uri[@xlink:href]" mode="jats2html">
    <a class="{local-name()}">
      <xsl:apply-templates select="@*" mode="#current"/>
      <xsl:apply-templates select="." mode="class-att"/>
      <xsl:apply-templates mode="#current"/>
      <xsl:if test="not(node())">
        <xsl:value-of select="@xlink:href"/>
      </xsl:if>
    </a>
  </xsl:template>

  <xsl:template match="@xlink:href" mode="jats2html">
    <xsl:attribute name="{if (contains(../name(), 'graphic')) then 'src' else 'href'}" 
                   select="if ($rr and matches(., '^\.\./'))
                           then resolve-uri(., resolve-uri($rr))
                           else tr:escape-html-uri(.)"/>
  </xsl:template>
  
  <xsl:template match="@ext-link-type" mode="jats2html"/>
  
  <xsl:template match="@xlink:type" mode="jats2html"/>

  <xsl:key name="by-id" match="*[@id]" use="@id"/>
  <xsl:key name="by-rid" match="*[@rid]" use="@rid"/>
  <xsl:key name="rule-by-name" match="css:rule" use="@name"/> 
  
  <xsl:variable name="root" select="/" as="document-node()"/>
  
  <xsl:template match="contrib/xref[@rid][not(node())]" mode="jats2html">
    <xsl:variable name="affiliation-ids" select="ancestor::contrib-group[1]/aff/@id" as="attribute(id)*"/>
    <xsl:variable name="index" select="index-of($affiliation-ids, @rid)" as="xs:integer*"/>
    <a class="aff-ref" href="#{@rid}" id="{(@id, generate-id())[1]}">
      <sup><xsl:value-of select="$index"/></sup>
    </a>
  </xsl:template>
  
  <xsl:template match="contrib-group/aff[@id]" mode="jats2html">
    <xsl:variable name="affiliations-ids" select="for $aff in parent::*/aff return ($aff/@id, generate-id($aff))[1]" as="xs:string+"/>
    <xsl:variable name="pos" select="index-of($affiliations-ids, (@id, generate-id())[1])" as="xs:integer"/>
    <p class="aff">
      <xsl:apply-templates select="@*" mode="#current"/>
      <span class="label">
        <xsl:value-of select="$pos"/>
      </span>
      <xsl:apply-templates mode="#current"/>
    </p>
  </xsl:template>

  <xsl:variable name="xref-start-string" select="'['" as="xs:string?"/>
  <xsl:variable name="xref-end-string" select="']'" as="xs:string?"/>
  
  <xsl:template match="xref" mode="jats2html">
    <xsl:param name="in-toc" as="xs:boolean?" tunnel="yes"/>
    <xsl:variable name="linked-items" as="element(linked-item)*">
      <xsl:apply-templates select="key('by-id', tokenize(@rid, '\s+'), $root)" mode="linked-item"/>
    </xsl:variable>
    <xsl:variable name="xref-id" select="(@id, generate-id())[1]" as="xs:string"/>
    <xsl:choose>
      <xsl:when test="node()">
        <!-- explicit referring text -->
        <xsl:choose>
          <xsl:when test="$in-toc">
            <xsl:apply-templates mode="#current"/>
          </xsl:when>
          <xsl:when test="count($linked-items) eq 1">
            <a href="#{$linked-items[1]/@id}">
              <xsl:apply-templates select="." mode="class-att"/>
              <xsl:if test="@id">
                <!-- in some cases an xref does not have an @id, so we will not create duplicate @id="xref_" attributes -->
                <xsl:attribute name="id" select="concat('xref_', @id)"/>  
              </xsl:if>
              <xsl:sequence select="tr:create-epub-type-attribute(.)"/>
              <xsl:apply-templates select="@srcpath, @alt, node()" mode="#current"/>
            </a>
            <xsl:if test="    $linked-items[1]/@ref-type = 'ref' 
                          and $bib-backlink-type = 'letter'
                          and not(text())"><!-- bibliography entry, render only symbol when no content exists in the 1st place -->
              <span class="cit">
                <xsl:apply-templates select="@srcpath" mode="#current"/>
                <xsl:value-of select="$xref-start-string"/>
                <xsl:number format="a" value="index-of( for $xr in key('by-rid', @rid, $root) 
                                                        return $xr/@id, @id )"/>
                <xsl:value-of select="$xref-end-string"/>
              </span>
            </xsl:if>
          </xsl:when>
          <!-- no items with matching @rid could be found -->
          <xsl:when test="count($linked-items) eq 0">
            <a>
              <xsl:apply-templates select="@srcpath" mode="#current"/>
            </a>
            <xsl:apply-templates mode="#current"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:message>Cannot link: multiple resolutions for xref with an explicit link text. <xsl:copy-of select="."/></xsl:message>
            <!-- content should not be lost though.-->
            <xsl:apply-templates mode="#current"/>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>
      <xsl:otherwise>
        <!-- generate referring text -->
        <a>
          <xsl:apply-templates select="@srcpath" mode="#current"/>
        </a>
        <xsl:call-template name="render-rids">
          <xsl:with-param name="linked-items" select="$linked-items"/>
          <xsl:with-param name="in-toc" select="$in-toc" tunnel="yes"/>
          <xsl:with-param name="xref-id" select="$xref-id" tunnel="yes"/>
        </xsl:call-template>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="xref" mode="class-att">
    <xsl:attribute name="class" separator=" ">
      <xsl:next-match/>
      <xsl:sequence select="local-name()"/>
    </xsl:attribute>
  </xsl:template>

  <xsl:template match="@alt" mode="jats2html">
    <xsl:attribute name="title" select="."/>
  </xsl:template>
  
  <xsl:template match="nav-pointer" mode="jats2html">
    <a href="#{@rid}" class="{local-name()}">
      <xsl:next-match/>
    </a>
  </xsl:template>
  
  <xsl:template name="render-rids">
    <xsl:param name="linked-items" as="element(linked-item)*"/>
    <xsl:param name="xref-id" as="xs:string" tunnel="yes"/>
    <xsl:variable name="grouped-items" as="element(linked-items)" xmlns="">
      <linked-items>
        <xsl:for-each-group select="$linked-items" group-by="@ref-type">
          <ref-type-group type="{current-grouping-key()}">
            <xsl:for-each-group select="current-group()" group-adjacent="jats2html:link-rendering-type(., ('label', 'number', 'title', 'teaser'))">
              <rendering type="{current-grouping-key()}">
                <xsl:variable name="context" select="." as="element(*)"/>
                <xsl:for-each select="current-group()/(@* | *)[name() = current-grouping-key()]">
                  <item id="{$context/@id}" xref-id="{$xref-id}">
                    <xsl:apply-templates select="." mode="render-xref"/>
                  </item>
                </xsl:for-each>
              </rendering>
            </xsl:for-each-group>  
          </ref-type-group>
        </xsl:for-each-group>
      </linked-items>
    </xsl:variable>
    <xsl:apply-templates select="$grouped-items" mode="render-xref"/>
  </xsl:template>

  <xsl:function name="jats2html:ref-type" as="xs:string">
    <xsl:param name="elt" as="element(*)"/>
    <xsl:choose>
      <xsl:when test="$elt/self::book-part">
        <xsl:sequence select="($elt/@book-part-type, $elt/name())[1]"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:sequence select="$elt/name()"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:function>


  <!-- Example:
       <linked-item number="4.2" label="Figure 4.2.">
         <title>Title, potentially including markup. If there is an alt-title[@alt-title-type eq 'xref'], it should be used</title>
         <teaser>The beginning of the contents, without index terms and footnotes</teaser>
       </linked-item>
  -->
  <xsl:template match="*" mode="linked-item" xmlns="">
    <linked-item>
      <xsl:copy-of select="@id"/>
      <xsl:attribute name="ref-type" select="jats2html:ref-type(.)"/>
      <xsl:variable name="title-container" as="element(*)">
        <xsl:choose>
          <xsl:when test="self::book-part">
            <xsl:sequence select="book-part-meta/title-group"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:sequence select="."/>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:variable>
      <xsl:for-each select="$title-container/alt-title[@alt-title-type eq 'number']">
        <xsl:attribute name="number" select="."/>
      </xsl:for-each>
      <xsl:for-each select="$title-container/label">
        <xsl:attribute name="label" select="."/>
      </xsl:for-each>
      <xsl:apply-templates select="($title-container/(title, alt-title[@alt-title-type eq 'xref']))[last()]" mode="#current"/>
      <teaser>
        <xsl:apply-templates mode="render-xref"/>
      </teaser>
    </linked-item>
  </xsl:template>
  
  <xsl:template match="title | alt-title[@alt-title-type eq 'xref']" mode="linked-item" xmlns="">
    <title>
      <xsl:apply-templates mode="render-xref"/>
    </title>
  </xsl:template>
  
  <xsl:function name="jats2html:link-rendering-type" as="xs:string">
    <xsl:param name="elt" as="element(linked-item)"/>
    <!-- preference: sequence of 'number', 'title', 'label', 'teaser' --> 
    <xsl:param name="preference" as="xs:string*"/>
    <xsl:sequence select="(for $p in $preference return $elt/(@* | *)[name() eq $p]/name(), '')[1]"/>
  </xsl:function>

  <xsl:template match="linked-items | ref-type-group" mode="render-xref">
    <xsl:apply-templates mode="#current"/>
  </xsl:template>
  
  <xsl:template match="ref-type-group[@type = ('sec', 'part', 'chapter')]/rendering[@type = ('title', 'number')]" mode="render-xref">
    <xsl:value-of select="key('l10n-string', if(count(item) gt 1) then ../@type else concat(../@type, 's'), $l10n)"/>
    <xsl:text>&#xa;</xsl:text>
    <xsl:for-each select="item">
      <xsl:apply-templates select="." mode="#current"/>
      <xsl:if test="position() lt last()">
        <xsl:text xml:space="preserve">, </xsl:text>
      </xsl:if>
    </xsl:for-each>
  </xsl:template>

  <xsl:template match="ref-type-group/rendering/item" mode="render-xref">
    <xsl:param name="in-toc" as="xs:boolean?" tunnel="yes"/>
    <xsl:choose>
      <xsl:when test="$in-toc">
        <xsl:apply-templates mode="#current"/>
      </xsl:when>
      <xsl:otherwise>
        <a href="#{@id}" id="xref_{@xref-id}">
          <xsl:apply-templates mode="#current"/>
        </a>    
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  
  <xsl:function name="jats2html:is-book-part-like" as="xs:boolean">
    <xsl:param name="elt" as="element(*)"/>
    <!-- add more: -->
    <xsl:sequence select="$elt/local-name() = ('toc', 
                                               'book-part', 
                                               'preface', 
                                               'foreword', 
                                               'dedication', 
                                               'front-matter-part',
                                               'book-app')"/>
  </xsl:function>
  
  <xsl:function name="jats2html:heading-level" as="xs:integer?">
    <xsl:param name="elt" as="element(*)"/>
    <xsl:apply-templates select="$elt" mode="jats:heading-level"/>
  </xsl:function>
  
  <xsl:template match="*" mode="jats:heading-level" as="xs:integer?">
    <xsl:message>No heading level for <xsl:copy-of select=".."/></xsl:message>
  </xsl:template>
  
  <xsl:template match="table-wrap/* | verse-group/* | fig/* | fig/caption/*" mode="jats:heading-level" as="xs:integer?"/>

  <xsl:template match="book-title-group/*" mode="jats:heading-level" as="xs:integer?">
    <xsl:sequence select="1"/>
  </xsl:template>

  <xsl:template match="title-group/* | index/* | index-title-group/* | fn-group/* | back/*" 
    mode="jats:heading-level" as="xs:integer?">
    <xsl:sequence select="2"/>
  </xsl:template>

  <xsl:template match="sec[ancestor::boxed-text]/*" mode="jats:heading-level" as="xs:integer?">
    <xsl:sequence select="count(ancestor::*[ancestor::boxed-text]) + 3"/>
  </xsl:template>

  <xsl:template match="abstract/* | def-list/* | trans-abstract/* | ack/* | app/* | app-group/* | bio/* |
                       glossary/* | sec/* | ref-list/* | statement/* | kwd-group/*" mode="jats:heading-level" as="xs:integer?">
    <xsl:variable name="ancestor-title" as="element(title)?" 
      select="(
                ../../( title
                        | (. | ../book-part-meta)/title-group/title)
              )[last()]" />
    <!-- last() because there were multiple ancestor-titles for /book-part/back[title]/app/title -->
    <xsl:variable name="heading-level" select="if(exists($ancestor-title))
                                               then jats2html:heading-level($ancestor-title) + 1
                                               else ()" as="xs:integer?"/>
    <xsl:sequence select="((if($heading-level gt 6) then 6 else $heading-level), 2)[1]"/>
  </xsl:template>


  <xsl:function name="jats2html:table-width-grid" as="xs:integer">
    <!-- returns 0, 50, or 100. It should be interpreted and used as a width
      percentage, except when it’s 0. Then the original widths should be kept. -->
    <xsl:param name="page-width-twip" as="xs:double"/>
    <xsl:param name="object-width-twip" as="xs:double"/>
    <xsl:choose>
      <xsl:when test="$object-width-twip gt 0.75 * $page-width-twip">
        <xsl:sequence select="100"/>
      </xsl:when>
      <xsl:when test="$object-width-twip gt 0.4 * $page-width-twip">
        <xsl:sequence select="50"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:sequence select="0"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:function>
  
  <!-- map alignment to CSS -->
  <xsl:template match="@valign" mode="hub2htm:css-style-overrides">
    <xsl:attribute name="css:vertical-align" select="."/>
  </xsl:template>

  <xsl:template match="@align" mode="hub2htm:css-style-overrides">
    <xsl:attribute name="css:text-align" select="."/>
  </xsl:template>
  
  <xsl:template match="@bgcolor" mode="hub2htm:css-style-overrides">
    <xsl:attribute name="css:background-color" select="."/>
  </xsl:template>
  
  <xsl:template match="@width" mode="hub2htm:css-style-overrides">
    <xsl:attribute name="css:width" select="."/>
  </xsl:template>
  
  <!-- if you want to omit metadata in your output, set the param $render-metadata to 'no' -->
  
  <xsl:template match="front" mode="jats2html" priority="4.5">
    <h1>
      <xsl:value-of select="article-meta/article-id" separator=" "/>
    </h1>
    <xsl:apply-templates mode="#current"/>
  </xsl:template>
  
  <!--  *
        * JATS/BITS metadata for <head> section
        * -->
  
  <!-- override this template in your importing stylesheet if you don't 
       want to enrich the HTML head with additional meta tags -->
  
  <xsl:template name="create-meta-tags">
    <xsl:apply-templates select="(collection-meta, book-meta)
                                |(front/journal-meta, front/article-meta)" mode="jats2html-create-meta-tags"/>
  </xsl:template>
  
  <xsl:template match="collection-meta|book-meta|journal-meta|article-meta" mode="jats2html-create-meta-tags">
    <xsl:apply-templates select="*" mode="jats2html-create-meta-tags"/>
  </xsl:template>
  
  <xsl:template match="pub-date[@publication-format]" mode="jats2html-create-meta-tags">
    <meta name="{concat(local-name(), '-', @publication-format)}" content="{concat(year, '-', month, '-', day)}"/>
  </xsl:template>
  
  <xsl:template match="pub-date[not(@publication-format)]" mode="jats2html-create-meta-tags">
    <meta name="{local-name()}" content="{concat(year, '-', month, '-', day)}"/>
  </xsl:template>
  
  <xsl:template match="*[local-name() = ('issn', 'issn-l')][@publication-format]" mode="jats2html-create-meta-tags">
    <meta name="{concat(local-name(), '-', @publication-format)}" content="{.}"/>
  </xsl:template>
  
  <xsl:template match="*[local-name() = ('issn', 'issn-l')][not(@publication-format)]" mode="jats2html-create-meta-tags">
    <meta name="{local-name()}" content="{.}"/>
  </xsl:template>
  
  <!-- Dublin Core metadata -->
  
  <xsl:template match="collection-meta/title-group/title
                      |collection-meta/title-group/subtitle
                      |book-title-group/book-title
                      |book-title-group/subtitle
                      |title-group/article-title
                      |title-group/subtitle
                      |trans-title-group/trans-title
                      |trans-title-group/trans-subtitle" mode="jats2html-create-meta-tags">
    <meta name="DCTERMS.title" content="{.}" />
  </xsl:template>
  
  <xsl:template match="publisher-name" mode="jats2html-create-meta-tags">
    <meta name="DCTERMS.publisher" content="{.}" />
  </xsl:template>
  
  <xsl:template match="contrib" mode="jats2html-create-meta-tags">
    <meta name="DCTERMS.contributor" content="{(string-name, 
                                                string-join((name/surname, name/given-names), ' '))[1]}" />
  </xsl:template>
  
  <xsl:template match="abstract|trans-abstract" mode="jats2html-create-meta-tags">
    <meta name="DCTERMS.abstract" content="{.}" />
  </xsl:template>
  
  <xsl:template match="subject" mode="jats2html-create-meta-tags">
    <meta name="DCTERMS.subject" content="{.}" />
  </xsl:template>
  
  <xsl:template match="isbn" mode="jats2html-create-meta-tags" priority="1">
    <meta name="DCTERMS.identifier" content="{.}"/>
  </xsl:template>
  
  <xsl:template match="article-id[@pub-id-type eq 'doi']
                      |book-id[@book-id-type eq 'doi']" mode="jats2html-create-meta-tags">
    <meta name="DCTERMS.identifier" content="{.}"/> 
  </xsl:template>
  
  <xsl:template match="article-categories" mode="jats2html-create-meta-tags">
    <meta name="DCTERMS.type" content="{.}"/> 
  </xsl:template>
  
  <xsl:template match="copyright-statement" mode="jats2html-create-meta-tags">
    <meta name="DCTERMS.rights" content="{.}"/>
  </xsl:template>
  
  <xsl:template match="copyright-year" mode="jats2html-create-meta-tags"/>
  
  <xsl:template match="copyright-holder" mode="jats2html-create-meta-tags">
    <meta name="DCTERMS.holder" content="{.}"/>
  </xsl:template>
  
  <xsl:template match="license" mode="jats2html-create-meta-tags">
    <xsl:apply-templates select="@xlink:href, @license-type, *" mode="#current"/>
  </xsl:template>
  
  <xsl:template match="license-p" mode="jats2html-create-meta-tags">
    <meta name="DCTERMS.license" content="{.}"/>
  </xsl:template>
  
  <xsl:template match="license/@xlink:href" mode="jats2html-create-meta-tags">
    <meta name="DCTERMS.license" content="{.}"/>
  </xsl:template>
  
  <xsl:template match="license/@license-type" mode="jats2html-create-meta-tags">
    <meta name="DCTERMS.accessRights" content="{.}"/>
  </xsl:template>
  
  <!-- drop metadata which is not applicable for meta tags -->
  
  <xsl:template match="aff
                      |aff-alternatives
                      |author-notes
                      |conference
                      |counts
                      |custom-meta-group
                      |funding-group
                      |history
                      |kwd-group
                      |notes
                      |related-article
                      |related-object
                      |supplementary-material
                      |x" mode="jats2html-create-meta-tags"/>
  
  <!-- default handler for meta-tags -->
  
  <xsl:template match="*" mode="jats2html-create-meta-tags" priority="-1">
    <xsl:choose>
      <xsl:when test="*">
        <xsl:apply-templates select="*" mode="#current"/>    
      </xsl:when>
      <xsl:when test="@xlink:href">
        <link rel="{concat(parent::*/local-name(), '-', local-name())}" href="{@xlink:href}"/>
      </xsl:when>
      <xsl:when test="text()">
        <meta name="{concat(parent::*/local-name(), '-', local-name())}" content="{.}"/>    
      </xsl:when>
      <xsl:otherwise>
        <xsl:message select="'jats2html: unmapped element:', local-name()"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  
  <!--  *
        * JATS/BITS metadata to be rendered in <body>s
        * -->
  
  <!-- resolve metadata wrappers -->
  
  <xsl:template name="render-metadata-sections">
    <xsl:apply-templates select="collection-meta
                                |book-meta
                                |book-part-meta
                                |front/journal-meta
                                |front/article-meta" mode="jats2html-render-metadata"/>
  </xsl:template>
  
  <xsl:template match="collection-meta
                      |book-meta
                      |book-part-meta
                      |journal-meta
                      |article-meta" mode="jats2html-render-metadata">
    <div class="{local-name()} jats-meta">
      <xsl:apply-templates select="@*, *" mode="#current"/>
    </div>
  </xsl:template>
  
  <!-- default handler for rendering all metadata -->
  
  <xsl:template match="*" mode="jats2html-render-metadata" priority="-1">
    <div class="{local-name()} jats-meta">
      <xsl:choose>
        <xsl:when test="*">
          <xsl:apply-templates select="@*, node()" mode="#current"/>
        </xsl:when>
        <xsl:when test="text()">
          <span class="{local-name()} jats-meta-name">
            <xsl:value-of select="local-name()"/>
          </span>
          <xsl:text>&#x20;</xsl:text>
          <span class="{local-name()} jats-meta-value">
            <xsl:apply-templates mode="#current"/>
          </span>
        </xsl:when>
        <xsl:when test="not(text()) and @*">
          <div class="{local-name()} jats-meta-attlist">
            <xsl:for-each select="@*">
              <span class="{local-name()} jats-meta-attname">
                <xsl:value-of select="."/>
              </span>
              <span class="{local-name()} jats-meta-attvalue">
                <xsl:value-of select="."/>
              </span>
            </xsl:for-each>  
          </div>
        </xsl:when>
        <xsl:otherwise>
          <xsl:apply-templates mode="#current"/>
        </xsl:otherwise>
      </xsl:choose>  
    </div>
  </xsl:template>
  
  <!--  *
        * render content metadata
        * -->
  
  <xsl:template match="collection-meta/title-group
                      |book-title-group" mode="jats2html-create-title">
    <div class="{local-name()}">
      <h1 class="{if(self::book-title-group) then 'book-title' else 'collection-title'}">
        <xsl:apply-templates select="@*, label, title, book-title" mode="#current"/>
      </h1>
      <xsl:apply-templates select="* except (label|title|book-title)" mode="#current"/>
    </div>
  </xsl:template>
  
  <xsl:template match="subtitle" mode="jats2html-create-title">
    <h2 class="{if(ancestor::collection-meta) then 'collection-subtitle' else local-name()}">
      <xsl:apply-templates select="@*, node()" mode="#current"/>
    </h2>
  </xsl:template>
  
  <xsl:template match="trans-title-group/title
                      |trans-title-group/trans-title" mode="jats2html-create-title">
    <h3 class="{local-name()}">
      <xsl:apply-templates select="@*, node()" mode="#current"/>
    </h3>
  </xsl:template>
  
  <xsl:template match="trans-title-group/subtitle
                      |trans-title-group/trans-subtitle" mode="jats2html-create-title">
    <h4 class="{local-name()}">
      <xsl:apply-templates select="@*, node()" mode="#current"/>
    </h4>
  </xsl:template>
  
  <xsl:template match="alt-title" mode="jats2html-create-title">
    <h5 class="{local-name()}">
      <xsl:apply-templates select="@*, node()" mode="#current"/>
    </h5>
  </xsl:template>
  
  <xsl:template match="contrib-group" mode="jats2html-create-title">
    <div class="{local-name()}">
      <xsl:for-each-group select="contrib" group-by="@contrib-type">
        <xsl:sort select="jats2html:sort-contrib(current-grouping-key())"/>
        <div class="{current-grouping-key()}">
          <xsl:apply-templates select="current-group()" mode="#current"/>
        </div>
      </xsl:for-each-group>
      <xsl:apply-templates select="* except contrib" mode="#current"/>
    </div>
  </xsl:template>
  
  <xsl:function name="jats2html:sort-contrib" as="xs:integer">
    <xsl:param name="contrib-type" as="xs:string?"/>
    <xsl:sequence select="     if(matches($contrib-type, 'editor', 'i')) then 2 
                          else if(matches($contrib-type, 'author', 'i')) then 1
                          else 0"/>
  </xsl:function>
  
  <xsl:template match="contrib" mode="jats2html-create-title">
    <p class="{concat(local-name(), ' ', @contrib-type)}">
      <xsl:apply-templates select="anonymous, (string-name, name)[1]" mode="#current"/>
      <xsl:apply-templates select="xref" mode="#current"/>
    </p>
  </xsl:template>
  
  <xsl:template match="contrib/xref" mode="jats2html-create-title">
    <xsl:variable name="ref" select="@rid" as="attribute(rid)"/>
    <xsl:variable name="aff" select="ancestor::contrib-group/aff[@id eq $ref]" as="element(aff)?"/>
    <xsl:if test="$aff">
      <p class="aff">
        <span class="{local-name()}">
          <xsl:apply-templates select="@*, $aff" mode="#current"/>  
        </span>
      </p>  
    </xsl:if>
  </xsl:template>
  
  <xsl:template match="aff" mode="jats2html-create-title">
    <xsl:analyze-string select="string-join(.//text(), '')" regex="([,;])">
      <xsl:matching-substring>
        <xsl:value-of select="regex-group(1)"/><br/>
      </xsl:matching-substring>
      <xsl:non-matching-substring>
        <xsl:value-of select="."/>
      </xsl:non-matching-substring>
    </xsl:analyze-string>
  </xsl:template>
  
  <xsl:template match="name" mode="jats2html jats2html-create-title">
    <span class="{local-name()}">
      <xsl:apply-templates select="@*, given-names" mode="#current"/>
      <xsl:text>&#xa;</xsl:text>
      <xsl:apply-templates select="surname" mode="#current"/>
    </span>
  </xsl:template>
  
  <xsl:template match="name-alternatives" mode="jats2html">
    <xsl:apply-templates select="(name[@xml:lang eq $lang], name[1])[1]" mode="#current"/>
  </xsl:template>
  
  <xsl:template match="email" mode="jats2html">
    <a href="{if(starts-with(@xlink:href, 'mailto:')) 
              then @xlink:href 
              else concat('mailto:', (@xlink:href, .)[1])}" class="email">
      <xsl:apply-templates select="@* except @xlink:href, node()" mode="#current"/>
    </a>
  </xsl:template>
  
  <xsl:template match="abstract|trans-abstract" mode="jats2html-create-title">
    <div class="{local-name()}">
      <xsl:apply-templates select="@*, node()" mode="jats2html"/>      
    </div>
  </xsl:template>

  <xsl:template match="kwd-group[not(@specific-use/tokenize(., ' ') = 'meta-only')][@kwd-group-type = ('author-created', 'author-generated')]" mode="jats2html-create-title jats2html">
    <div class="{local-name()} {@kwd-group-type}">
      <xsl:apply-templates select="@*, node()" mode="jats2html"/>
    </div>
  </xsl:template>

  <xsl:template match="kwd-group/kwd" mode="jats2html">
    <xsl:if test="preceding-sibling::kwd and not(preceding-sibling::*[1][self::x][matches(., '[,;]')])">
      <span class="kwd_sep">
        <xsl:text xml:space="preserve">; </xsl:text>
      </span>
    </xsl:if>
    <span class="kwd">
      <xsl:apply-templates mode="#current"/>
    </span>
  </xsl:template>

  <xsl:template match="article-meta/kwd-group[@kwd-group-type = 'abbreviations']" mode="jats2html-create-title jats2html">
    <dl class="{local-name()} {@kwd-group-type}">
      <xsl:apply-templates select="@* except @kwd-group-type, node()" mode="jats2html"/>
    </dl>
  </xsl:template>

  <xsl:template match="compound-kwd" mode="jats2html-create-title jats2html">
    <xsl:apply-templates mode="#current"/>
  </xsl:template>

  <xsl:template match="compound-kwd-part" mode="jats2html-create-title jats2html">
    <xsl:element name="{if(not(preceding-sibling::compound-kwd-part)) then 'dt' else 'dd'}">
     <xsl:attribute name="class" select="concat(local-name(), ' pos', count(preceding-sibling::compound-kwd-part) + 1)"/>
      <xsl:apply-templates select="@*, node()" mode="#current"/>
    </xsl:element>
  </xsl:template>
  
  <xsl:template match="volume-in-collection" mode="jats2html-create-title">
    <p class="{local-name()}">
      <xsl:apply-templates select="volume-title" mode="jats2html-create-title"/>
      <xsl:text>&#xa;</xsl:text>
      <xsl:apply-templates select="volume-number" mode="jats2html-create-title"/>
    </p>
  </xsl:template>
  
  <!-- everything that goes into a <p> -->

  <xsl:template match="funding-group
                      |award-group" mode="jats2html">
    <div class="{local-name()}">
      <xsl:call-template name="css:content"/>
    </div>
  </xsl:template>
  
  <xsl:template match="funding-source
                      |funding-statement" mode="jats2html jats2html-create-title">
    <p class="{local-name()}">
      <xsl:call-template name="css:content"/>
    </p>
  </xsl:template>
  
  <xsl:template match="funding-source[@xlink:href]" mode="jats2html jats2html-create-title">
    <p class="{local-name()}">
      <a>
        <xsl:call-template name="css:content"/>
      </a>
    </p>
  </xsl:template>
  
  <!-- default handler for creating simple divs and spans with *[@class eq local-name()]-->
  
  <xsl:template match="author-notes
                      |award-group
                      |funding-group
                      |fn-group
                      |publisher
                      |string-name
                      |trans-title-group" mode="jats2html-create-title">
    <div class="{local-name()}">
      <xsl:apply-templates select="@*, node()" mode="#current"/>
    </div>
  </xsl:template>
  
  <xsl:template match="collection-meta/title-group/title
                      |book-title-group/book-title
                      |collection-meta/title-group/label
                      |book-title-group/label
                      |anonymous
                      |given-names
                      |publisher-name
                      |surname
                      |volume-title
                      |volume-number" mode="jats2html-create-title">
    <span class="{local-name()}">
      <xsl:apply-templates select="@*, node()" mode="#current"/>
    </span>
  </xsl:template>
  
  <xsl:template match="isbn|issn|issn-l" mode="jats2html-create-title">
    <div class="{local-name()}">
      <xsl:apply-templates select="@*" mode="#current"/>
      <span class="{local-name()}-name">
        <xsl:value-of select="upper-case(local-name())"/>
      </span>
      <xsl:text>&#xa;</xsl:text>
      <span class="{local-name()}-value">
        <xsl:apply-templates mode="#current"/>
      </span>
    </div>
  </xsl:template>
  
  <!-- Drop stuff that is mentioned already in the metadata. Override this if you want to render this -->
  
  <xsl:template match="award-id
                      |collection-id
                      |book-id
                      |orcid-id
                      |funding-id
                      |subj-group
                      |object-id
                      |pub-date
                      |notes
                      |kwd-group
                      |funding-group/award-group" mode="jats2html-create-title"/>
  
  <!-- drop all attributes which are not matched by other templates -->
  
  <xsl:template match="@*" mode="jats2html-create-title"/>

  <xsl:function name="jats2html:contains-token" as="xs:boolean">
    <xsl:param name="string" as="xs:string?"/>
    <xsl:param name="token" as="xs:string+"/>
    <xsl:sequence select="tokenize($string, '\s+') = $token"/>
  </xsl:function>

  <xsl:template name="create-loi">
    <xsl:if test="$jats2html:create-loi and exists(//fig[caption])">
     <xsl:element name="{if ($epub-version = 'EPUB3' or $xhtml-version = '5.0') then 'section' else 'div'}">
       <xsl:attribute name="epub:type" select="'loi'"/>
       <xsl:attribute name="id" select="'loi'"/>
       <xsl:if test="$jats2html:loi-as-nav">
         <xsl:attribute name="hidden" select="'hidden'"/>
         <xsl:attribute name="class" select="'as-nav'"/>
       </xsl:if>
       <h1 class="lof-heading">
         <xsl:value-of select="if (/*/@xml:lang = 'de') then 'Abbildungsverzeichnis' else 'List of Figures'"/>
       </h1>
      <xsl:variable name="figures" as="element(*)*">
        <xsl:apply-templates select="//fig[caption]" mode="lof"/>
      </xsl:variable>
       <xsl:if test="exists($figures)">
         <ol>
           <xsl:for-each select="$figures">
             <xsl:sequence select="."/>
           </xsl:for-each>
         </ol>
       </xsl:if>
     </xsl:element>
    </xsl:if>
  </xsl:template>

  <xsl:template name="create-lot">
    <xsl:if test="$jats2html:create-lot and exists(//table-wrap[caption])">
     <xsl:element name="{if ($epub-version = 'EPUB3' or $xhtml-version = '5.0') then 'section' else 'div'}">
       <xsl:attribute name="epub:type" select="'lot'"/>
       <xsl:attribute name="id" select="'lot'"/>
       <xsl:if test="$jats2html:lot-as-nav">
         <xsl:attribute name="hidden" select="'hidden'"/>
         <xsl:attribute name="class" select="'as-nav'"/>
       </xsl:if>
       <h1 class="lof-heading">
         <xsl:value-of select="if (/*/@xml:lang = 'de') then 'Tabellenverzeichnis' else 'List of Tables'"/>
       </h1>
       <xsl:variable name="tables" as="element(*)*">
        <xsl:apply-templates select="//table-wrap[caption]" mode="lof"/>
      </xsl:variable>
       <xsl:if test="exists($tables)">
         <ol>
           <xsl:for-each select="$tables">
             <xsl:sequence select="."/>
           </xsl:for-each>
         </ol>
       </xsl:if>
     </xsl:element>
    </xsl:if>
  </xsl:template>
  
  <xsl:template match="table-wrap | fig" mode="lof">
    <xsl:if test="label[normalize-space()] or caption/title[normalize-space()]">
      <li>
        <a href="#{(@id, generate-id(.))[1]}">
          <xsl:apply-templates select="label" mode="strip-indexterms-etc"/>
          <xsl:apply-templates select="label" mode="label-sep"/>
          <xsl:apply-templates select="caption/title" mode="strip-indexterms-etc"/>
        </a>
      </li>
    </xsl:if>  
  </xsl:template>
      
</xsl:stylesheet>
