import * as dotenv from 'dotenv'
dotenv.config()

import * as vision from '@google-cloud/vision'
import * as fs from 'fs/promises'
import { createHash } from 'crypto'
import express from 'express'
import multer from 'multer'

import { createCanvas , loadImage } from 'canvas'

const upload = multer()

const app  = express()

app.use( express.json() )
app.use( express.urlencoded({ extended: true }) )
app.use( express.static('uploads') )


async function main( ) {

   
    let dirs = await fs.readdir('.')
    if (!dirs.includes("out")) fs.mkdir('./out')
    if (!dirs.includes("images")) fs.mkdir('./images')
    if (!dirs.includes("cache")) fs.mkdir('./cache')


    const client = new vision.ImageAnnotatorClient()

    app.get('/', async ( req , res ) => {
        res.send(
            "hello world"
        )
    })

    app.get('/cup', async ( req , res ) => {
        let size = Number.parseInt( req.query.size as string ) 
        let id = createHash('md5').update( Date() + (Math.random() * 1000000).toString() ).digest('hex')
    })



    app.post('/read', upload.single('pic') , async ( req , res ) => {

        // let rawimgdata = req.file 

        // if (!rawimgdata)
        //     return res.status(400).send('invalid params')

        // console.log( rawimgdata )
        // let imgdata = Buffer.from(rawimgdata,'base64')

        let imgdata = req.file?.buffer

        if (!imgdata)
            return res.status(400).send('invalid params')

        console.debug("recive image")            

        let hash = createHash('md5').update(imgdata).digest('hex')
        
        console.debug("create dir hash " + hash )            

        const rootpath = './cache/' + hash
        const imgpath = rootpath + '/' + 'img.jpg'


        if (!(await fs.readdir('./cache/')).includes(hash))
            await fs.mkdir( rootpath )

        console.debug("start write image to local disk" )            

        await fs.writeFile( imgpath , imgdata )

        console.debug("end write image to local disk" )            

        console.log("start textDetection")

        const [ result ] = await client.textDetection( imgdata )

        console.log("end textDetection")

        const img = await loadImage( imgdata ) 
        const canvas = createCanvas( img.width , img.height )
        const ctx = canvas.getContext("2d")

        ctx.drawImage(img , 0 , 0 )
        console.log("start box fulltext")
        if ( result.fullTextAnnotation?.pages ){

            for ( const text of result.fullTextAnnotation.pages ) {

                if (!text.blocks)
                    continue

                for ( const block of text.blocks ) {
                    let bbs = block.boundingBox
                    if (!bbs || !bbs.normalizedVertices )
                        continue

                    let vert = bbs.vertices
                    if (!vert)
                        continue
                    let paths = [
                            vert[0] , vert[1] ,
                            vert[1] , vert[2] ,
                            vert[2] , vert[3] ,
                            vert[3] , vert[0] ,
                    ]


                    ctx.strokeStyle = "rgba(255,0,0,0.5)"
                    ctx.lineWidth = 5 

                    ctx.beginPath()
                    
                    paths.forEach( p => ctx.lineTo(p.x!,p.y!)  )

                    ctx.stroke()

                }

            }

            

        }

        console.log("end box fulltext")

        type MedInfo = {
            name?: string,
            amount? : number,
            meal? : string,
            routine? : string
        }

        let _med_info : MedInfo = {}
        let med_info : string[] | undefined = undefined;
        console.log('start scrape data')
        if ( result.fullTextAnnotation?.text ) {
            let text = result.fullTextAnnotation?.text

            const amount = /(?<n>\d*)\sเม็/g
            const name = /(\d*)\s(mg|มก\.)/ig
            const routine = /(?<meal>ก(\w?)อน|หลัง)อาหาร (?<time>(เช้า\s?)?(เที่ยง\s?)?(เย็น\s?)?)/g

           
            let banner_index = 9999

            const results = text.split('\n').filter( ( v , i ) => {

                if (v.includes("หาด") && banner_index == 9999)
                    banner_index = i


                if ( banner_index > i )
                    return false

                console.log(banner_index,i,v)

                let amount_matcn = amount.exec( v )
                let name_match = name.exec( v )
                let routine_match = routine.exec( v )

                if ( !_med_info.name &&  name_match ) {
                    _med_info.name = v  
                    console.log( 'n' , _med_info.name )
                }
                else if ( !_med_info.amount && amount_matcn && !v.includes("รับ")  ) {
                    _med_info.amount = Number.parseInt( amount_matcn.groups?.n as string )
                    console.log( 'a' , _med_info.amount )
                }
                else if ( routine_match ) {
                    _med_info.routine = routine_match.groups?.time as string
                    _med_info.meal = routine_match.groups?.meal as string
                    console.log( 'r' , _med_info.routine )
                    console.log( 'm' , _med_info.meal )
                }

                return (v && amount.exec( v ) || name.exec( v ) || routine.exec( v ) ) 
            })

            med_info = results
        }

        console.log('end scrape data')

        console.log('start box text anno')
        if ( result.textAnnotations)
            for ( const text of result.textAnnotations ) {
                let vert = text.boundingPoly?.vertices
                if ( vert ) {
                    let paths = [
                            vert[0] , vert[1] ,
                            vert[1] , vert[2] ,
                            vert[2] , vert[3] ,
                            vert[3] , vert[0] ,
                    ]

                    ctx.strokeStyle = "rgba(0,255,0,0.5)"
                    ctx.lineWidth = 5 

                    ctx.beginPath()
                
                    paths.forEach( p => ctx.lineTo(p.x!,p.y!)  )

                    ctx.stroke()
                }
        }

        console.log('end box text anno')
        console.log('start write detect.png')
        await fs.writeFile(`${rootpath}/detect.png` , canvas.toBuffer("image/png") )
        console.log('end write detect.png')
        console.log('start write full.txt')
        await fs.writeFile(rootpath + '/full.txt' , result.fullTextAnnotation?.text ?? "invalid")
        console.log('end write full.txt')

        res.json({
            text : result.fullTextAnnotation?.text ?? "-1",
            hash : hash,
            _med_info
        })

    })

    app.listen( process.env.API_PORT , () => console.log('listen to ' + process.env.API_PORT ) )



}


Promise.all(
    [
        main()
    ]
)
