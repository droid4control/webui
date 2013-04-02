var refreshPage = function() {
		var xhr = new XMLHttpRequest();
		xhr.open('GET', '/pacui.json', false);
		xhr.send(null);

		var mbstatus = eval("(" + xhr.responseText + ")");

		// Create list of register types
		var regtypes = [];
		var typecontainer = document.getElementById('typecontainer');
		var newli1 = document.createElement('li');
		newli1.setAttribute('style', 'margin-left: 0px;');j
		newli1.innerHTML += '<div class="noframe"><div class="oc100"><div class="ic"></div></div></div>';
		for (var i = 0, lni = mbstatus.device_status.length; i < lni; i ++) {
			nextstatus: for (var j = 0, lnj = mbstatus.device_status[i].channel_data.length; j < lnj; j++) {
				var rtype = mbstatus.device_status[i].channel_data[j].typename;
				for (var k = 0; k < regtypes.length; k++) {
					if (regtypes[k] === rtype) {
						break nextstatus;
					}
				}
				regtypes.push(rtype);
				newli1.innerHTML += '<div><div class="frame2" style="width: 30px;"><div class="oc tname"><div class="ic">' + rtype + '</div></div></div></div>';
			}
		}
		if (typecontainer.hasChildNodes) {
			oldli = document.getElementById('typecontainer').childNodes[0];
			typecontainer.replaceChild(newli1, oldli);
		} else {
			typecontainer.ppendChild(newli1);
		}

		// Iterate all controllers
		for (var i = 0, lni = mbstatus.device_status.length; i < lni; i ++) {
			var cname =  mbstatus.device_status[i].name;
			var caddr =  mbstatus.device_status[i].address;
			var cstatus =  mbstatus.device_status[i].status;
			var cloc = (typeof mbstatus.device_status[i].location !== 'undefined') ? mbstatus.device_status[i].location : '';
			// Controller name
			var div1 = document.createElement('div');
			div1.innerHTML = '<div class="frame status' + cstatus + '"><div class="oc100"><div class="ic">' + cname + ((cloc !== '') ? (' (' + cloc + ')') : '') + '</div></div></div>';
			// Register map
			var div2 = document.createElement('div');
			// Read registers in regtypes order
			nextregline: for (var ri = 0; ri < regtypes.length; ri++) {
				// Register lines
				var lnj = mbstatus.device_status[i].channel_data.length;
				for (var j = 0; j < lnj; j++) {
					rtype = mbstatus.device_status[i].channel_data[j].typename;
					var div3  = document.createElement('div');
					if (rtype !== regtypes[ri])
						continue;
					// Registers for one line
					for (var k = 0, lnk = mbstatus.device_status[i].channel_data[j].data.length; k < lnk; k++) {
						var craddr = mbstatus.device_status[i].channel_data[j].data[k].address;
						if (typeof mbstatus.device_status[i].channel_data[j].data[k].bit !== 'undefined') {
							craddr += '.' + mbstatus.device_status[i].channel_data[j].data[k].bit;
						}
						var rstatus = 3;
						if (typeof mbstatus.device_status[i].channel_data[j].data[k].status !== 'undefined')
							rstatus = mbstatus.device_status[i].channel_data[j].data[k].status;
						var rvalue = mbstatus.device_status[i].channel_data[j].data[k].value;

//						div3.innerHTML += '<div class="frame2"><div class="oc status' + rstatus + '"><div class="ic1">' + craddr + '</div><div class="ic2">' + rvalue + '</div></div></div>';
						div3.innerHTML += '<div class="frame2 status' + rstatus + '"><div class="oc2"><div class="ic1">' + craddr + '</div></div> <div class="oc2"><div class="ic2">' + rvalue + '</div></div></div>';
					}
					div2.appendChild(div3);
					continue nextregline;
				}
				// This type does not exist, fill with transparent box
				div3.innerHTML += '<div class="frame2" style="border: 0px; margin: 2px;"><div class="oc"><div class="ic"></div></div></div>';
				div2.appendChild(div3);
			}
			// create new <LI> and insert DIVs
			var newli = document.createElement('li');
			newli.setAttribute('style', 'margin-right: 5px;');
			newli.appendChild(div1);
			newli.appendChild(div2);
			document.getElementById('devcontainer').appendChild(newli);
		}
		// Iterate status indicators
		var innerHtml = '';
		for (var i = 0, lni = mbstatus.modbusproxy_status.indicator.length; i < lni; i ++) {
			var iname = mbstatus.modbusproxy_status.indicator[i].name;
			var istatus = mbstatus.modbusproxy_status.indicator[i].status;
			innerHtml += '<div class="frame3"><div class="oc paramstate status' + istatus + '"><div class="ic">' + iname + '</div></div></div>' + "\n";
		}
		document.getElementById('statuscontainer').innerHTML = innerHtml;
		// Iterate info
		innerHtml = ''
		for (var i = 0, lni = mbstatus.modbusproxy_status.info.length; i < lni; i ++) {
			var iname = mbstatus.modbusproxy_status.info[i].name;
			var ivalue = mbstatus.modbusproxy_status.info[i].value;
			innerHtml += '<div class="frame3"><div class="oc infoframe"><div class="ic">' + iname + ' : ' + ivalue + '</div></div></div>' + "\n";
		}
		document.getElementById('infocontainer').innerHTML = innerHtml;
};

refreshPage();

setInterval(function() {
	refreshPage();
}, 1000);
