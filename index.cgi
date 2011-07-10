#!/usr/bin/perl

#Perl Script to Auto Generate Websites
#Copyright (C) 2004 Jack Elston

#This program is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

#Jack Elston
#elstonj@colorado.edu

use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser);
use LWP::Simple;
use Switch;

#--------USER INPUT---------
eval(`cat config`);
#--------USER INPUT---------

$input = new CGI;
$dir = $input->param('dir');
$num = $input->param('num');
$perpage = $input->param('perpage');
$session = $input->param('session');
$section = $input->param('section');
$template = $input->param('template');

if(!$template) {$template = $defaultTemplate;}
if(! -e "$templateDir/$template.html") {$template = $defaultTemplate;}

$resultPage = `cat "$templateDir/$template.html"`;
#&make_styles();
#
&log_in();
if(!$loggedIn) {if($dir =~ /\./) {$dir = "";}}
if(! -d "$rootDir/$dir") {$dir="";}

if(`ls -lag "$rootDir/$dir"| head -n 2| tail -n 1| grep 'drwxrwxrwx\\|apache'` ) {
  $editable = 1;
  &edit_files();
  &editable_dirs();
}

$formVars = "<input type=\"hidden\" name=\"dir\" value=\"$dir\">
<input type=\"hidden\" name=\"num\" value=\"$num\">
<input type=\"hidden\" name=\"perpage\" value=\"$perpage\">
<input type=\"hidden\" name=\"section\" value=\"$section\">
<input type=\"hidden\" name=\"template\" value=\"$template\">";

&make_styles();
&make_tabs();

if($dir) {
  $currentDir = $dir;
  $currentDir =~ s/$page\///g;
  $baseDir = "$rootDir/$page";
  if($page) {$root = "$page/";}
  push(@menus,
    &make_menu(
      &list_directories($baseDir, $currentDir),
      "folders"));
}

chdir "$rootDir/$dir";
my $isExternHTML = `ls |grep .html|wc -l`;
$isExternHTML = $isExternHTML + `ls |grep .php|wc -l`;

if($isExternHTML > 1) {&make_extern_html("$baseHref$dir");}
elsif(-e "text.html") {&make_doc_page("$rootDir/$dir");}
elsif(-e "text,v") {&make_cvs_page("$rootDir/$dir");}
elsif(-e "index.html") {$content = `cat index.html`}
elsif(-e "index.php") {$content = `cat index.php`}
elsif(-e "index.cgi") {eval `cat index.cgi`;}
elsif(-e "index.bib") {&make_pubs_page("$rootDir/$dir");}
else {&make_files_page("$rootDir/$dir");}

if($lcolumn ne "" ) {
  $lcolumn=join($lcolumn,"<td id=\"left-column\">","</td>");
}
if($rcolumn ne "") {
  $rcolumn=join($rcolumn,"<td id=\"right-column\">","</td>");
}

foreach (@menus) {$menus=$menus."\n".$_;}

  #-----[ print page ]-----#

$footer = '
  <div class="padding">&nbsp;</div>
    <div id="footer">
      Website by elstonj himself : 
      Jack Elston
    </div>
  </div>';

$title = "
  <h1 id=\"logo\">
    <a href=\"\">
		$title
    </a>
  </h1>";

$resultPage=~s/<!-- head -->/$head/g;
$resultPage=~s/<!-- body -->/$body/g;
$resultPage=~s/<!-- title -->/$title/g;
$resultPage=~s/<!-- tabs -->/$tabs/g;
$resultPage=~s/<!-- menus -->/$menus/g;
$resultPage=~s/<!-- header -->/$header/g;
$resultPage=~s/<!-- content -->/$content/g;
$resultPage=~s/<!-- footer -->/$footer/g;

print"Content-type:text/html\n\n";
print $resultPage; 
exit;

#------------------make_styles()-----------------------
sub make_styles {
  @styles = `find $templateDir/ -name *.html -printf "\%f\\n"`;
  if(!scalar(@styles)) {return;}

	my $styles="";
  foreach (@styles) {
    $_ = (split /\./, $_)[0];
    my $image = "homegray.gif";
    if($_ eq $style) {$image="home.gif";}
    
    my $cgiOut = "?dir=$dir&num=$num&perpage=$perpage&section=$section&session=$session&template=$_";
    $styles = join("",$styles,"\n\r<img src=\"/images/$image\">\n\r<a href=\"$pathToScript$cgiOut\">$_</a>");
  }                    
  $styles = join($styles,"styles: ","");
  push(@menus,&make_menu($styles,"Styles"));
}

#------------------make_tabs()-----------------------
sub make_tabs {
  $page = (split(/\//,$dir))[0];

  if($loggedIn) {
    @pages = ("home/\n",`ls -AF $rootDir |grep \"[/@]\"`);
  }
  else {
    @pages = ("home/\n",`ls -F $rootDir |grep \"[/@]\"`);
  }
  chop @pages; chop @pages;
	$tabs="";

  foreach (@pages) {
    my $select = "plain";
    my $tempName = $_;
    $tempName =~ s/\.//g;
    if($_ eq $page) {$select="selected";}
    my $cgiOut = "?dir=$_&num=&perpage=$perpage&section=&session=$session&template=$template";
    $tabs = join("",$tabs,"\n    <li class=\"$select\">\n      <a href=\"$pathToScript$cgiOut\">$tempName</a>\n    </li>");
  }                    
  $tabs = join($tabs,"<div id=\"tab\">","</div>");
}

#------------------make_menu()-----------------------
sub make_menu {
  if(@_[0] eq "") {return;}
  my $id = lc @_[1];
  $id =~ s/ //g;
  my $menuhtml = join(@_[0],"
    <div id=\"$id\" class=\"menu\">
      <h5>@_[1]</h5>
      <div class='menuBody'>
        ","
      </div>
      <div class='menuFooter'></div>
    </div>");
  return $menuhtml;
}

#----------------make_menu_item()--------------------
sub make_menu_item {
  my $item=
    "<a href=\"@_[1]\"
    style=\"padding-left: @_[3];display:block\">
    <img src=\"images/@_[2].gif\"
    @_[0]
    </a>";
  return $item;
}

#----------------list_directories()-------------------
sub list_directories{
  my $current=$currentDir;
  my $base=$baseDir;
  my $recur=$recurse;
  $sub_dirs="";

  $recurse = $recurse+1;

  my @current_dirs=split /\//, $current;
  my $r=$root;

  if($base=~m/$current/) {}
  else {if($recurse > 10) {
    $content="overflow<br>base = $base current = $current<br>";
    return;
  }
  else {
    if($r ne "") {$root="$root@current_dirs[$recur]/";}
    else {$root="@current_dirs[$recur]/";}
    &list_directories(
      $currentDir="$current",
      $baseDir="$base/@current_dirs[$recur]",
      $base_cgi=$base_cgi,
      $recurse=$recurse);
  }}

  $space=join("",($recur*0.5),"em");
  chdir $base;
  my $dirs ="";

  if($loggedIn) {@dirs = `ls -AF -I \".tn\" -I \"*.*\" |grep \"[/@]\"`; }
  else {@dirs = `ls -F -I \"*.*\"|grep \"[/@]\"`;}
  foreach (@dirs) {
    chop $_;
    chop $_;
    my $tempName = $_;
    $tempName =~ s/\.//g;
    if($_ eq @current_dirs[$recur]) {
      my $cgiOut = "?dir=$r$_&num=&perpage=$perpage&section=&session=$session&template=$template";
      $dirs=join("",$dirs,&make_menu_item(
        $tempName,
        "$pathToScript$cgiOut",
        "openfolder",
        $space),$sub_dirs);
    }
    elsif($_ ne ".cap") {
      my $cgiOut = "?dir=$r$_&num=&perpage=$perpage&section=&session=$session&template=$template";
      $dirs=join("",$dirs,&make_menu_item(
        $tempName,
        "$pathToScript$cgiOut",
        "folder",
        $space));
    }
  }
  $sub_dirs=$dirs;
}

#-----------------make_files_page()--------------------
sub make_files_page{

  chdir @_[0];

  @files = (<*.*>);
  if(scalar(@files) == 0) {
    @files = `find ./ -iname "*.jpg" -printf "\%TY\%Tm\%Td\%TH\%TM\%TS@\%p\\n"|grep -v .tn|sort -r|head|cut -d @ -f 2|cut -c 2-`;
    @recentFiles = @files;
    $editable = 0;
    $arePics = 1;
    if(scalar(@files) == 0) {$content = "&nbsp"; return;}
  }
  else {
    if(!`find .tn/*.* -printf "\%f\\n"|sort > /tmp/out$$; find *.* -printf "\%f\\n" |sort> /tmp/out2$$;diff -b /tmp/out$$ /tmp/out2$$;rm /tmp/out$$ /tmp/out2$$;`) {$arePics = 1;}}

  if($arePics)
  {
    if($num eq "") {$num = 1;}
    if($perpage eq "") {$perpage=9}
    $tempDir = $dir;
    $tempDir =~ s/ /%20/g;
  
    $numpages=int(scalar(@files)/$perpage);
    if((scalar(@files) % $perpage) > 0) {$numpages=$numpages+1;}
    if($num*$perpage > scalar(@files)) {$num=$numpages;}
    my $count = 0;
    
    #---navigation buttons---
    $navigation;
    my $i=1;
    $prev=$num-1;
    $next=$num+1;

    $navigation=join("",$navigation,"<table width=\"100%\"><tr>");
  
    if($prev != 0) {
      my $cgiOut = "?dir=$tempDir&num=$prev&perpage=$perpage&section=$section&session=$session&template=$template";
      $navigation=join("",$navigation,"<td><a href=$pathToScript$cgiOut>prev</a></td><td>");
    }
    else {$navigation=join("",$navigation,"<td>prev</td><td>");}
    while($numpages >= $i) {
      if($num == $i) {
        $navigation=join("",$navigation,"$i ");
      }
      else {
        my $cgiOut = "?dir=$tempDir&num=$i&perpage=$perpage&section=$section&session=$session&template=$template";
        $navigation=join("",$navigation,"<a href=$pathToScript$cgiOut>$i</a> ");
      }
      $i = $i + 1;
    }
    if($next <= $numpages) {
      my $cgiOut = "?dir=$tempDir&num=$next&perpage=$perpage&section=$section&session=$session&template=$template";
      $navigation=join("",$navigation,"</td><td><a href=$pathToScript$cgiOut>next</a></td></tr></table>");
    }
    else {
      $navigation=join("",$navigation,"</td><td>next</td></tr></table>");
    }
    #---navigation buttons---

#  if(!@recentFiles) {
#    @recentFiles = `find ./ -iname "*.jpg" -printf "\%TY\%Tm\%Td\%TH\%TM\%TS@\%p\\n"|grep -v .tn|sort -r|head|cut -d @ -f 2|cut -c 2-`;}
#  foreach (@recentFiles){
#      $name=(split /\//, $_)[-1];
#      $file_list = join("<a href=\"$baseHref$dir$_\" style=\"text-decoration:none\"><img src=\"images/pic.gif\"> $name",$file_list,"</a><br>\n");}
#    $rcolumn = join("",$rcolumn,
#      &make_menu($file_list,"Recently Added Images"));
}

  @iconTypes = `ls $rootDir/../images/icons/ | cut -d . -f 1`;

  foreach $file (@files) {
    $date = "";
    @fileDir=split /\//, $file;
    $file = pop(@fileDir);
    chomp $file;
    $preDir = join("/",@fileDir);
    if($arePics) {
      if($count == $perpage*$num) { last; }
      elsif($count < $perpage*($num-1)) { $count++; next; }
    }
    if($editable) {&editable_files();}
    $class = "captionedPicture";

    if($tn = -e ".$preDir/.tn/$file") {
      $img = "$baseHref$dir$preDir/.tn/$file$ext";
      if(!$loggedIn || !$editable) {$class = "floatleft";}
        #$date = `cat -v ".$preDir/$file"|head -n 1`;
        #$date =~ /(\d\d\d\d):(\d\d):(\d\d).(\d\d:\d\d:\d\d)/;
        #if($2 ne "") {
          #$date = "$2/$3/$1<br>\n$4<br>\n";}
    }
    else {
      $extension = (split /\./, $file)[-1];
      #if($extension eq "jpg") {
        #$date = `cat -v ".$preDir/$file"|head -n 1`;
        #$date =~ /(\d\d\d\d):(\d\d):(\d\d).(\d\d:\d\d:\d\d)/;
        #if($2 ne "") {
          #$date = "$2/$3/$1<br>\n$4<br>\n";}
      #}
      my $knownType =0;
      foreach(@iconTypes) {
        if("$extension\n" eq $_) {$knownType=1;}}
      if(!$knownType){$extension = "unk";}
      $img = "images/icons/$extension.gif";
    }

    if($cap = -e ".$preDir/.cap/$file.txt" || $date) {
      $cap = `cat ".$preDir/.cap/$file.txt"`;
      $cap = "<td width=100% valign=\"top\">$date$cap</td>";
      $class = "captionedPicture";
    }
    if(!$cap && !$tn) {$cap = "<td width=100%>$file<td>";}

    $content = join("",$content,"
      <table class=\"$class\">
        <tr valign=top>
          <td><a href=\"$baseHref$dir$preDir/$file\"><img src=\"$img\"></a></td>
          $cap
          $editForm
        </tr>
      </table>");

    $count++;
  }

  $content = join($content, "<table width=\"100%\"><tr><td>$navigation</td></tr><tr><td>", "</td></tr><tr><td>$navigation</td></tr></table>");

  if($preDir) {
    $content=join("","<h2> Recently Added Images</h2><br>",$content);
  }

  if($arePics) {
    for($i= 2; $i < 7; $i = $i + 1) {
      $val = $i * $i;
      my $cgiOut = "?dir=$tempDir&num=$num&perpage=$val&section=$section&session=$session&template=$template";
      $numpage=join("",$numpage,&make_menu_item(
        $val,
        "$pathToScript$cgiOut",
        "homegray",
        "0.0em"));
    }

    push(@menus,&make_menu($numpage,"Images Per Page"));
  }
}

#------------------editable_files()--------------------
sub editable_files {
  if($loggedIn) {
    my $formOut = "
    <input type=\"hidden\" name=\"dir\" value=\"$dir\">
    <input type=\"hidden\" name=\"num\" value=\"$num\">
    <input type=\"hidden\" name=\"perpage\" value=\"$perpage\">
    <input type=\"hidden\" name=\"section\" value=\"$section\">
    <input type=\"hidden\" name=\"session\" value=\"$session\">
    <input type=\"hidden\" name=\"template\" value=\"$template\">
    <input type=\"hidden\" name=\"file\" value=\"$file\">";
    $editForm = "
    <td width=100%>
    <form action=\"$pathToScript\" method=\"post\">
      <td>Change Caption</td>
      $formOut
      <td><input type=\"text\" name=\"caption\" size=\"20\"></textarea></td>
      <td><input type=\"image\" src=\"images/checkbox.gif\"></td>
    </form>
    </td><td>
    &nbsp&nbsp&nbsp&nbsp&nbsp&nbsp
    </td><td>
    <form action=\"$pathToScript\" method=\"post\" onsubmit=\"return confirm('Are you sure you want to delete this file?')\">
      <input type=\"hidden\" name=\"delpic\" value=\"1\">
      $formOut
      <input type=\"image\" src=\"images/trash.gif\" alt=\"delete folder\">
    </form>
    </td>
    ";
  }
}

#------------------make_doc_page()--------------------
sub make_doc_page {
  chdir @_[0];
  @cont= `cat text.html`;

  my $start=0;
  foreach(@cont) {

    if($start==0)  {
      if($_=~/<h3>$section/) {$start=1;}
      if($section eq "") {$start=2;}
    }
    if($start>0) {
      if($_=~/<h3>/) {$start += 1;}
      if($start<3) {
        $content=join(" ",$content,$_);
        if($_=~/<h4>/) {
          $_=~s/<h4>|<\/h4>|\n|://g;
          my $cgiOut = "?dir=$dir&num=$num&perpage=$perpage&session=$session&template=$template&section=$section#$_";
          $menu=join("",$menu,
            &make_menu_item("$_", "$pathToScript$cgiOut", "homegray", "1.0em"));
        }
      }
    }

    if($_=~/<h3>/ && !($_=~/Table of Contents/)) {
      $_=~s/<h3>|<\/h3>|\n|://g;
      my $cgiOut = "?dir=$dir&num=$num&perpage=$perpage&section=$_&session=$session&template=$template";
      $menu=join("",$menu,
        &make_menu_item("$_", "$pathToScript$cgiOut", "homegray", "0.0em"));
    }
  }
  $content=join($content,"<div class='text'>","</div>");
  push(@menus,&make_menu($menu,"Table of Contents"));
}

#-----------------editable_dirs()--------------------
sub editable_dirs{
  if($loggedIn) {
    my $formOut = "
    <input type=\"hidden\" name=\"dir\" value=\"$dir\">
    <input type=\"hidden\" name=\"num\" value=\"$num\">
    <input type=\"hidden\" name=\"perpage\" value=\"$perpage\">
    <input type=\"hidden\" name=\"section\" value=\"$section\">
    <input type=\"hidden\" name=\"session\" value=\"$session\">
    <input type=\"hidden\" name=\"template\" value=\"$template\">
    <input type=\"hidden\" name=\"file\" value=\"$file\">";

    push(@menus,&make_menu("
    <form action=\"$pathToScript\" method=\"post\">
      Create Folder:<br><hr>
      <input type=\"text\" name=\"createdir\">
      $formOut<br><br>
      <input type=\"image\" src=\"images/checkbox.gif\">
    </form><br><br>
    <form action=\"$pathToScript\" method=\"post\" onsubmit=\"return confirm('Are you sure you want to delete this folder and all of its contents?')\">
      Remove Current Directory:<br><hr>
      <input type=\"hidden\" name=\"rmdir\" value=\"1\">
      $formOut
      <input type=\"image\" src=\"images/trash.gif\">
    </form><br><br>
    <form action=\"$pathToScript\" enctype=\"multipart/form-data\" method=\"post\">
      Create File:<br><hr>
      <input type=\"file\" name=\"createfile\">
      $formOut<br><br>
      <input type=\"image\" src=\"images/checkbox.gif\">
    </form><br><br>$error","edit directory"));
  }
}

#-------------------edit_files()----------------------
sub edit_files{
  if($loggedIn) {
    chdir "$rootDir/$dir";
    if($input->param("createdir") ne "") {
      my $createdir = $input->param("createdir");
      $createdir =~ s/ /\\ /g;
      `mkdir $createdir`;
      `chmod 777 $createdir`;
    }
    elsif($input->param("rmdir") eq "1") {
      $tempDir = (split(/\//,$dir))[-1];
      $dir =~ s/\/$tempDir//g;
      chdir "$rootDir/$dir";
      `rm -rf "$tempDir"`;
    }
    elsif($input->param("createfile") ne "") {
      $file = $input->param("createfile");
      $maxUploadFileSize *= 1024;
      $fileName = $file;
      $fileType   = (split(/\./, $fileName))[-1];
      $fileName   = (split(/\./, $fileName))[-2];

      $fileName =~ s/^.*(\\|\/)//;
      if($fileName =~ /\W/) {$fileName =~ s/\W//ig;}
      $fileName = "$fileName.$fileType";

      for($i = 0; $i < scalar(@uploadTypes); $i++){
        if(lc($fileType) eq @uploadTypes[$i]){$typeOk = 1;}
      }
      $typeOk = 1;
     
      if($typeOk) {
        if(open(NEW, ">$fileName")) {
          while (read($file, $buffer, 1024)) {print NEW $buffer;}
          close NEW;
        }
        else {$error =  "Error: Could not open new file on server."; return;}
        if(-s $fileName > $maxUploadFileSize) {
          `rm -f "$fileName"`;
          $error = "Error: File exceeded limitations : $fileName";
          return;
        }
      }
      else {$error = "Error: Bad file type : $fileType"; return;}

      if(-s $fileName) {
        if($fileType eq "jpg") {
          system ("mkdir .tn") if (!-d ".tn");
          system ("/usr/bin/./convert -geometry 200x200 -quality 30 \"$fileName\" \".tn/$fileName\"");
        }
        $error = "Success";
        return;
      }
      else {
        `rm -f "$fileName"`;
        $error = "Error: No data in $fileName. No size on server''s copy of file.  Check the path entered.";
      }
    }
    if($file = $input->param("file")) {
      if($input->param("caption") ne "") {
        system ("mkdir .cap") if (!-d ".cap");
        open(OUTFILE,"> .cap/$file.txt");
        print OUTFILE $input->param("caption");
        close OUTFILE;
      }
      else {`rm -f ".cap/$file.txt"`;}
      if($input->param("delpic") eq "1") {
        `rm -f ".cap/$file.txt"`;
        `rm -f "$file"`;
        `rm -f ".tn/$file"`;
      }
    }
  }
}

#------------------make_cvs_page()--------------------
sub make_cvs_page {
  my $menu=`tac /usr/local/cvs/CVSROOT/history|grep -v \\* |head`;
  my @lines=split /^/,$menu;
  $menu="";
  foreach(@lines) {
    my @columns=split /\|/,$_;
    $menu=join(" ",$menu,"<tr><td>@columns[1]</td><td>@columns[3]</td><td>@columns[4]</td><td>@columns[5]</td>");
  }
  $menu=join($menu,"<table cellpadding=5><tr><td>User</td><td>Folder</td><td>Version</td><td>File</td></tr><tr><td colspan=4><hr></td></tr>","</table>");

  $rcolumn=join("",$rcolumn,
    &make_menu($menu,"Recent Changes"));

  chdir @_[0];
  my @cont= `cat text,v`;
  my $start=0;
  my $mark=0;
  foreach(@cont) {
    if ($start == 1) {
      if($_=~/@/) {$mark=$mark+1;if($mark==2){last}}
      else {$content=join(" ",$content,$_);}
    }
    if ($_=~/text/) {$start=1};
  }
}

#----------------make_extern_html()-------------------
sub make_extern_html {
  $content="<div class='text'>
    <iframe class=\"iframe\" frameborder=no border=0 framespacing=0 scrolling=yes src=\"@_[0]\" width=100% height=100%>
    Your browser doesn't support iframes
    </iframe></div>";
}

#---------------------log_in()------------------------
sub log_in {
  $loggedIn = 0;
  if(!$session) {
    @passwds = `cat $passwordFile`;
    foreach (@passwds) {
      chomp;
      ($user, $pass, $key) = split /:/;
      if(($user eq param('user')) && ($pass eq (crypt(param('pass'), $key)))){
        $loggedIn = 1;
      }
    }

    if($loggedIn) {
      my $lower = 0;
      my $upper = 65535;
      $session = int(rand( $upper-$lower+1 ) ) + $lower;
      $time = `date +%s`;
  
      open(FILE,">>$sessionFile");
      print FILE "$session:$time";
      close FILE;
    }
  }
  else {
    @sessions = `cat $sessionFile`;
    $time = `date +%s`;
    my $sessionsFile = "";
    foreach (@sessions) {
      chomp;
      if($_) {
        ($sessionnum, $secs) = split /:/;
        if(($time - $secs) < $loginTimeOut) {
          if($sessionnum eq $session) {
            $sessionsFile = join("",$sessionsFile,"$session:$time"); 
            $loggedIn = 1;
          }
          else {
            $sessionsFile = join("",$sessionsFile,"$sessionnum:$secs\n"); 
          }
        }
      }
    }
    open(FILE,">$sessionFile");
    print FILE $sessionsFile;
    close FILE;
  }
  if(!$loggedIn) {
    $session = "";
    my $menu = "
      <form action=\"$pathToScript\" method=\"post\">
      username:<br>
      <input type=\"text\" name=\"user\"><br>
      password:<br>
      <input type=\"password\" name=\"pass\"><br><br>
      $formVars
      <input type=\"Submit\" value=\"submit\">
      </form>";
    push(@menus,&make_menu($menu,"Log In"));
  }
  else {$head = "<meta http-equiv=\"refresh\" content=\"1805\">";}
}

#------------------make_pubs_page()--------------------
sub make_pubs_page {
	if($section eq "bib") {
		&return_bib();
	} else {

	%entries = ();
  chdir @_[0];
  @content = `cat index.bib`;
	foreach $line (@content) {
		if($line =~ m/^\s*@/) {
			$ext = "pdf";

			($type,$name) = split(/\{/,$line);
			$name =~ s/\s*,\s*\n//;
			$type =~ s/^.(.*)/$1/;
			$type = lc($type);
			switch ($type) {
				case "inproceedings" {$type = "Conference";}
				case "inbook" {$type = "Book Chapter";}
				case "article" {$type = "Journal";}
				case "phdthesis" {$type = "Thesis";}
				else {$type = "Defense"; $ext = "pptx";}
			}
		}
		if($line =~ m/^\s*author\s*=/) {
			$line =~ m/\{(.*)\}/;
			$author = $1;
			$first_author = (split(/ and/,$author))[0];
			$first_author =~ s/ \w\. / /g;
			if ($first_author =~ m/,/) {
				$last_name = (split(/, /,$first_author))[0];
			} else {
				$last_name = (split(/ /,$first_author))[1];
			}
			$author =~ s/ and/,/g;
		}
		if($line =~ m/^\s*title\s*=/) {
			$line =~ m/\{(.*)\}/;
			$pubtitle = $1;
		}
		if($line =~ m/^\s*booktitle\s*=/) {
			$line =~ m/\{(.*)\}/;
			$booktitle = $1;
		}
		if($line =~ m/^\s*journal\s*=/) {
			$line =~ m/\{(.*)\}/;
			$booktitle = $1;
		}
		if($line =~ m/^\s*school\s*=/) {
			$line =~ m/\{(.*)\}/;
			if($type eq "Thesis") {
				$booktitle = "Ph.D. Thesis, $1";
			}
			if($type eq "Defense") {
				$booktitle = "Ph.D. Defense, $1";
			}
		}
		if($line =~ m/^\s*year\s*=/) {
			$line =~ m/\{(.\d*)\}/;
			$year = $1;
		}
		if($line =~ m/^\s*month\s*=/) {
			$line =~ m/\{(.*)\}/;
			$month = $1;
		}
		if($line =~ m/^\s*url\s*=/) {
			$line =~ m/\{(.*)\}/;
			$url = $1;
		}
		if($line =~ m/^\s*note\s*=/) {
			$line =~ m/\{(.*)\}/;
			$note = $1;
		}
		if($line =~ m/^\s*volume\s*=/) {
			$line =~ m/\{(.\d*)\}/;
			$volume = $1;
		}
		if($line =~ m/^\s*number\s*=/) {
			$line =~ m/\{(.\d*)\}/;
			$number = "($1)";
		}
		if($line =~ m/^\s*pages\s*=/) {
			$line =~ m/\{(.*)\}/;
			$pages = ":$1";
		}
		if($line =~ m/^\s*project\s*=/) {
			$line =~ m/\{(.*)\}/;
			$project = $1;
		}
		if($line =~ m/^\}$/) {
			if($volume ne "" || $pages ne "" || $number ne "") {
				$extra = " $volume$number$pages,"
			}
			$html = "
				<table class=\"captionedPicture\"> 
					<tr valign=top> 
						<td width=\"40px\">
							<a href=\"$url\">
								<img src=\"images/icons/$ext.gif\">
							</a>
							<a href=\"$pathToScript?dir=$dir&section=bib&bibentry=$name\">
								<img src=\"images/icons/bib.gif\">
							</a>
						</td> 
						<td valign=\"top\">
							$author<br>
							<i>$pubtitle</i><br> 
							<span style=\"color:#AAA;\">$booktitle,$extra $month $year.</span><br>
							<span style=\"color:yellow;\">$note</span>
						</td> 
					</tr> 
				</table> 
				</a><br><br><br>";
      $rev_year = 3000-$year;
      %mon2num = qw("non" "00" jan "01"  feb "02"  mar "03"  apr "04"  may "05"  jun "06" jul "07"  aug "08"  sep "09"  oct "10" nov "11" dec "12" );
      if($month eq "") {$month="none";}
      $month_num = $mon2num{lc substr($month, 0, 3) };
      switch ($type) {
        case "Thesis" {$priority=1;}
        case "Defense" {$priority=2;}
        case "Journal" {$priority=3;}
        case "Book Chapter" {$priority=4;}
        case "Conference" {$priority=5;}
      }
			switch ($section) {
				case "author" {$entries{"$last_name$rev_year$month_num:$first_author:$name"} = $html;}
        case "date" {$entries{"$rev_year$month_num:$year:$name"} = $html;}
        case "type" {$entries{"$priority:$type:$year$name"} = $html;}
				case "project" {$entries{":$project:$priority$rev_year}$name"} = $html;}
				else {$entries{"$rev_year$month_num:$year:$name"} = $html; $section="date";}
			}
			$ext = ""; $author=""; $pubtitle=""; $booktitle=""; $month=""; $year=""; $note=""; $html=""; $first_author=""; $last_name=""; $extra=""; $volume=""; $number=""; $pages=""; $project=""; $rev_year=""; $priority=""; $month_num="";
		}
	}

	$last_category = "";

  foreach $key (sort keys %entries ) {
    $category = (split(/:/,$key))[1];
    if($category ne $last_category) {
      $content = join("<h1>$category</h1>",$content,"<br>");
      $last_category = $category;
    }
    $content = join($entries{$key},$content,"<br>");
  }
	}


	switch ($section) {
		case "date" {@items = ("home","homegray","homegray","homegray");}
		case "author" {@items = ("homegray","home","homegray","homegray");}
		case "type" {@items = ("homegray","homegray","home","homegray");}
		case "project" {@items = ("homegray","homegray","homegray","home");}
		else {@items = ("homegray","homegray","homegray","homegray");}
	}

	$navigation=join("",
			&make_menu_item(
				"publication year",
				"$pathToScript?section=date&dir=$dir",
				$items[0],
				"0.0em"),
			&make_menu_item(
				"first author",
				"$pathToScript?section=author&dir=$dir",
				$items[1],
				"0.0em"),
			&make_menu_item(
				"publication type",
				"$pathToScript?section=type&dir=$dir",
				$items[2],
				"0.0em"),
			&make_menu_item(
				"research project",
				"$pathToScript?section=project&dir=$dir",
				$items[3],
				"0.0em"),
			);

    push(@menus,&make_menu($navigation,"Sort By"));
}

#------------------return_bib()--------------------
sub return_bib {
	$entry = $input->param('bibentry');

  chdir @_[0];
  @content = `cat index.bib`;
	$recording = 0;
	$bib = "";
	foreach $line (@content) {
		if($line =~ m/^\s*@.*$entry,\s*$/) {
			$recording = 1;
		}
		if ($recording) {
				$line =~ s/^\s*(@\w*)\s*\{\s*(\w*),/<span style="color:cyan;">$1<\/span>{<span style="color:#F80">$2<\/span>,/g;
			if(!($line =~ m/^\s*url\s*=/)) {
				$line =~ s/^\s*(\w*)\s*=/&nbsp&nbsp<span style="color:yellow;">$1<\/span>=/g;
				$bib = join($line,$bib,"<br>");
			}
			if($line =~ m/^\}$/) {
				$recording = 0;
			}
		}
	}

	$content = $bib;
}
