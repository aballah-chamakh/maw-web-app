import './AppContent.scss' ;
import OrderLoader from './OrderLoader/OrderLoader';
import OrderSubmitter from './OrderSubmitter/OrderSubmitter';
import GenericTable from '../CommonComponents/GenericTable/GenericTable' ;
import ServerLoading from '../CommonComponents/ServerLoading/ServerLoading';
import { useState } from 'react';


import { Routes,Route } from 'react-router-dom';

const AppContent = (props)=>{
    const [nb,setNb] = useState({nb:10})
    let keys = ['selected','id','first and last name','city','delegation','locality','carrier']
    let orders =[
      {
          "id": 511,
          "id_carrier": "23",
          "transaction_id": false,
          "address_detail": {
              "city": "Medenine",
              "delegation": "Beni Khedache",
              "locality": "",
              "address1": "testing testting",
              "phone_mobile": "22222222222"
          },
          "customer_detail": {
              "firstname": "test",
              "lastname": "test",
              "email": "test22@gmail.com"
          },
          "cart_products": [
              {
                  "name": "Bain d'huile cheveux bouclés",
                  "quantity": "1"
              }
          ],
          "total_paid": "23.000000",
          "carrier": "AFEX",
          "selected": true
      },
      {
          "id": 512,
          "id_carrier": "23",
          "transaction_id": false,
          "address_detail": {
              "city": "Tunis",
              "delegation": "El Ouerdia",
              "locality": "Bellevue",
              "address1": "Rue de la Meuse ",
              "phone_mobile": "24656754"
          },
          "customer_detail": {
              "firstname": "Mariem",
              "lastname": "Ben nejma",
              "email": "mariem.bennejma19@gmail.com"
          },
          "cart_products": [
              {
                  "name": "Pack cheveux secs et abîmés",
                  "quantity": "1"
              }
          ],
          "total_paid": "100.800000",
          "carrier": "AFEX",
          "selected": true
      },
      {
          "id": 513,
          "id_carrier": "23",
          "transaction_id": false,
          "address_detail": {
              "city": "Sfax",
              "delegation": "Sfax Ville",
              "locality": "Sfax",
              "address1": "Route De Tunis Immeuble Dar Attabib",
              "phone_mobile": "54757997"
          },
          "customer_detail": {
              "firstname": "Héla",
              "lastname": "Zribi",
              "email": "helazribi93@gmail.com"
          },
          "cart_products": [
              {
                  "name": "DUO REVEIL BOUCLES",
                  "quantity": "1"
              }
          ],
          "total_paid": "79.900000",
          "carrier": "AFEX",
          "selected": true
      },
      {
          "id": 514,
          "id_carrier": "23",
          "transaction_id": false,
          "address_detail": {
              "city": "Beja",
              "delegation": "Mejez El Bab",
              "locality": "Mejez El Bab",
              "address1": "cité 13 aout",
              "phone_mobile": "99169060"
          },
          "customer_detail": {
              "firstname": "ebdelli",
              "lastname": "mariem",
              "email": "meriemebdelli17102002@gmail.com"
          },
          "cart_products": [
              {
                  "name": "Le duo cheveux gras et pellicules",
                  "quantity": "1"
              }
          ],
          "total_paid": "46.600000",
          "carrier": "AFEX",
          "selected": true
      },
      {
          "id": 515,
          "id_carrier": "23",
          "transaction_id": false,
          "address_detail": {
              "city": "Ben Arous",
              "delegation": "Ben Arous",
              "locality": "Ben Arous",
              "address1": "14 rue khaled ibn walid ben arous",
              "phone_mobile": "29780239"
          },
          "customer_detail": {
              "firstname": "Taissir",
              "lastname": "Ben moumen",
              "email": "Taissir.benmoumen12@gmail.com"
          },
          "cart_products": [
              {
                  "name": "Brume capillaire Kasméri",
                  "quantity": "1"
              }
          ],
          "total_paid": "27.000000",
          "carrier": "AFEX",
          "selected": true
      }
  ]

  let dropdown_keys = {
    'carrier' : ['AFEX','LOXBOX']
  }

  let highlight_keys ={'id':'red'}
    return(
        <div className="app-content-container">

          <Routes>
                    <Route path="/load_orders" element={<OrderLoader />} />
                    <Route path="/load_orders/:orders_loader_id/submit_orders" element={<OrderSubmitter />} />
                    <Route path="/generic_table" element={<GenericTable keys={keys} orders={orders} dropdown_keys={dropdown_keys} highlight_keys={highlight_keys}  />} />
          </Routes>
          
        </div>
    )
}
export default AppContent ;
