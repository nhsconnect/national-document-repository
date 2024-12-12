/*
import React, { useEffect } from 'react';

type Props = {
	fileUrl: string;
}

const PdfJsApp: React.FC<Props> = ( { fileUrl } ) => {

	useEffect( () => {

			const script = document.createElement('script');
			script.src = '/pdfjs/srcVersion/web/viewer.mjs';
			script.type = 'module';
			document.body.appendChild(script);

		const viewerContainer = document.getElementById('viewerContainer');

		if (viewerContainer) {

		const fileUrlValue = encodeURIComponent('./test.pdf');
		const viewerHtml = `/pdfjs/srcVersion/web/viewer.html?file=${fileUrlValue}`;

			fetch(viewerHtml)
				.then( (response) => response.text() )
				.then( (html) => {

					viewerContainer.innerHTML = html;

					const scripts = viewerContainer.querySelectorAll('script');
					scripts.forEach( (inlineScript)  => {

						const newScript = document.createElement('script');
						newScript.type = 'module';
						newScript.textContent = inlineScript.textContent;
						document.body.appendChild(newScript);
						document.body.removeChild(newScript);

					}	);

				})
		}

		return () => {
				document.body.removeChild(script);
		};

	}, [fileUrl] );

	return ( 

		<div
			id="viewerContainer"
			style={{
				height: '800px',
				width: '800px'
			}}
		>
		</div>

 	);

};

export default PdfJsApp;

*/
