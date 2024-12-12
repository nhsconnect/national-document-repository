
 // git clone pdf.js src/ or a release/ version

 // compile … yarn build generic ? … copy -recursive
 // build/ and web/

 // 
 // public / pdfjs/
 // └── srcVersion
 //  ├── build
 //  ├── LICENSE
 //  └── web
 //

import React from 'react';

type Props = {
	fileUrl: string
}

const PdfJsIframe: React.FC<Props> = ( { fileUrl } ) => {

	return (

			<iframe
				src={`/pdfjs/srcVersion/web/viewer.html?file=${encodeURIComponent(fileUrl)}`}
				style={{
					margin: ' 100px 0px 0px 0px',
					width: '100%', 
					height: '600px'}}
				title="title title"
			/>

 	)

};

export default PdfJsIframe;
