import React from 'react';

class ErrorBoundary extends React.Component {
  state = {
    errorMessage: '',
  };

  static getDerivedStateFromError(error) {
    return { errorMessage: error };
  }

  componentDidCatch(error, info) {
    console.log('from the error boundry')
    console.log(error, info.componentStack);
  }



  render() {
    if (this.state.errorMessage) {
      return <p style={{'color':'red',margin:'20px',fontSize:'20px'}} >{ this.state.errorMessage.toString() }</p>;
    }
    return this.props.children;
  }
}

export default ErrorBoundary;